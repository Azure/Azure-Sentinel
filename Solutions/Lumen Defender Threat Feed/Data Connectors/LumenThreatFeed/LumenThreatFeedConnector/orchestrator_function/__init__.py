import logging
import os
from datetime import timedelta
import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context):
    """Enhanced orchestrator with dynamic work distribution and progress tracking."""
    try:
        input_data = context.get_input() or {}

        if not input_data:
            raise ValueError("No input data provided to orchestrator")

        # Basic controls
        run_id = input_data.get('run_id', 'unknown')
        indicators_per_request = int(input_data.get('indicators_per_request', 100))
        max_concurrent = int(input_data.get('max_concurrent_activities', os.environ.get('LUMEN_MAX_CONCURRENT_ACTIVITIES', '10')))
        continue_after_units = int(os.environ.get('LUMEN_CONTINUE_AFTER_UNITS', '50'))

        # Manifest paging and optional legacy direct-list support
        manifest_blob_name = input_data.get('manifest_blob_name')
        page_offset = int(input_data.get('page_offset', 0))
        page_size = int(input_data.get('page_size', int(os.environ.get('LUMEN_MANIFEST_PAGE_SIZE', '500'))))
        unit_start_index = int(input_data.get('unit_start_index', 0))
        blob_sources = input_data.get('blob_sources', [])

        # Accumulate totals across ContinueAsNew cycles
        summary_accum = input_data.get('summary_accum', {
            'uploaded': 0,
            'errors': 0,
            'throttles': 0,
            'work_units_completed': 0,
        })

        # Work units can be provided for resume; otherwise build from manifest or blob_sources
        work_units = input_data.get('work_units')
        if work_units is None:
            work_units = []
            if manifest_blob_name:
                page = yield context.call_activity('activity_get_manifest_page', {
                    'manifest_blob_name': manifest_blob_name,
                    'offset': page_offset,
                    'limit': page_size,
                })
                items = page.get('items', [])
                items_to_process = items[unit_start_index:] if unit_start_index > 0 else items
                for source in items_to_process:
                    work_units.append({
                        'blob_name': source['blob_name'],
                        'indicator_type': source.get('indicator_type', 'unknown'),
                        'indicators_per_request': indicators_per_request,
                        'run_id': run_id,
                        'work_unit_id': f"{run_id}-{source.get('indicator_type','x')}-{source['blob_name']}",
                        'process_all': True,
                        # internal backoff by default inside activity
                    })
                has_more = bool(page.get('has_more', False))
                next_offset = int(page.get('next_offset', page_offset + len(items)))
            else:
                for source in blob_sources:
                    work_units.append({
                        'blob_name': source['blob_name'],
                        'indicator_type': source.get('indicator_type', 'unknown'),
                        'indicators_per_request': indicators_per_request,
                        'run_id': run_id,
                        'work_unit_id': f"{run_id}-{source.get('indicator_type','x')}-{source['blob_name']}",
                        'process_all': True,
                        # internal backoff by default inside activity
                    })
                has_more = False
                next_offset = 0

        total_work_units = len(work_units)

        # Execute with limited parallelism (fan-out/fan-in per batch)
        results = []
        total_throttle_events = 0
        batch_size = max_concurrent
        index = 0
        processed_since_continue = 0

        while index < len(work_units):
            # Important: slice by remaining, not assumed batch_size
            batch = work_units[index:index + batch_size]
            batch_num = (index // batch_size) + 1
            total_batches = (len(work_units) + batch_size - 1) // batch_size

            tasks = [context.call_activity('activity_upload_from_blob', inp) for inp in batch]
            results_batch = yield context.task_all(tasks)

            batch_throttle = 0
            throttled_inputs = []
            max_retry_after = 0
            cleaned_up = 0
            for inp, res in zip(batch, results_batch):
                if isinstance(res, dict) and res.get('throttled'):
                    retry_after = int(res.get('retry_after', 60))
                    max_retry_after = max(max_retry_after, retry_after)
                    batch_throttle += int(res.get('throttle_events', 0))
                    throttled_inputs.append(inp)
                    continue

                yield context.call_activity('activity_cleanup_blob', {
                    'blob_name': inp['blob_name'],
                    'run_id': run_id,
                })
                cleaned_up += 1
                results.append(res)

            if throttled_inputs:
                backoff_seconds = min(max_retry_after if max_retry_after > 0 else 60, 300)
                logging.info(
                    f"Throttled by Sentinel: backing off {backoff_seconds}s; "
                    f"requeueing {len(throttled_inputs)} work unit(s)"
                )
                yield context.create_timer(context.current_utc_datetime + timedelta(seconds=backoff_seconds))
                work_units.extend(throttled_inputs)

            total_throttle_events += batch_throttle
            total_uploaded_so_far = sum((r or {}).get('uploaded_count', 0) for r in results)
            logging.debug(f"Progress: Blob batch {batch_num}/{total_batches} - {total_uploaded_so_far:,} uploaded")

            processed_since_continue += cleaned_up

            # No mid-page ContinueAsNew: finish all requeued items in this page

            # Advance by actual batch length so that any re-appended throttled work
            # will still be picked up by the while condition.
            index += len(batch)

        total_uploaded = sum((r or {}).get('uploaded_count', 0) for r in results)
        total_errors = sum((r or {}).get('error_count', 0) for r in results)

        # Combine with accumulator to produce unified totals across continues
        cumulative_uploaded = summary_accum.get('uploaded', 0) + total_uploaded
        cumulative_errors = summary_accum.get('errors', 0) + total_errors
        cumulative_throttles = summary_accum.get('throttles', 0) + total_throttle_events
        cumulative_units = summary_accum.get('work_units_completed', 0) + processed_since_continue

        logging.info("=== ORCHESTRATION COMPLETE ===")
        logging.info(f"Run ID: {run_id}")
        logging.info(f"This segment — work units: {total_work_units}, uploaded: {total_uploaded}, errors: {total_errors}, throttles: {total_throttle_events}")
        logging.info(
            f"CUMULATIVE — work units completed: {cumulative_units}, "
            f"uploaded: {cumulative_uploaded}, errors: {cumulative_errors}, throttles: {cumulative_throttles}"
        )
        logging.info(f"Blob sources processed (if legacy path): {len(blob_sources)}")

        if 'has_more' in locals() and has_more and manifest_blob_name:
            logging.info(f"Paging manifest: advancing to next page at offset {next_offset}")
            # Fold this segment's totals into the accumulator before paging to next
            segment_uploaded = sum((r or {}).get('uploaded_count', 0) for r in results)
            segment_errors = sum((r or {}).get('error_count', 0) for r in results)
            segment_throttles = total_throttle_events
            segment_units = processed_since_continue
            new_summary = {
                'uploaded': summary_accum.get('uploaded', 0) + segment_uploaded,
                'errors': summary_accum.get('errors', 0) + segment_errors,
                'throttles': summary_accum.get('throttles', 0) + segment_throttles,
                'work_units_completed': summary_accum.get('work_units_completed', 0) + segment_units,
            }
            new_input = {
                'run_id': run_id,
                'indicators_per_request': indicators_per_request,
                'max_concurrent_activities': max_concurrent,
                'manifest_blob_name': manifest_blob_name,
                'page_offset': next_offset,
                'page_size': page_size,
                'summary_accum': new_summary,
            }
            context.continue_as_new(new_input)
            return

    # No final safety carry-over: rely on manifest paging and unit_start_index

        return {
            'success': True,
            'run_id': run_id,
            'total_work_units': total_work_units,
            'segment_uploaded': total_uploaded,
            'segment_errors': total_errors,
            'segment_throttle_events': total_throttle_events,
            'cumulative_uploaded': cumulative_uploaded,
            'cumulative_errors': cumulative_errors,
            'cumulative_throttle_events': cumulative_throttles,
            'cumulative_work_units_completed': cumulative_units,
            'blob_sources_processed': len(blob_sources),
        }

    except Exception as e:
        logging.error(f"Orchestrator error: {type(e).__name__}: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'run_id': run_id if 'run_id' in locals() else 'unknown',
        }

# Create the orchestrator function binding 
main = df.Orchestrator.create(orchestrator_function)
