import logging
import azure.durable_functions as df
from datetime import timedelta

TARGET_MAX_REQUESTS_PER_MIN = 95


def orchestrator_function_v3(context: df.DurableOrchestrationContext):
    try:
        input_data = context.get_input()
        sources = input_data['blob_sources']
        config = input_data['config']
        per_request = input_data.get('indicators_per_request', 100)

        work_units = []
        max_per_unit = 1000
        for s in sources:
            est = s['estimated_indicators']
            if est <= 0:
                continue
            parts = (est + max_per_unit - 1) // max_per_unit
            for i in range(parts):
                start = i * max_per_unit
                size = min(max_per_unit, est - start)
                work_units.append({
                    'blob_name': s['blob_name'],
                    'indicator_type': s['indicator_type'],
                    'start_index': start,
                    'max_indicators': size,
                    'work_unit_id': f"{s['indicator_type']}-{i+1}",
                    'config': config,
                    'indicators_per_request': per_request
                })

        batch_size = 3
        results = []
        for batch_start in range(0, len(work_units), batch_size):
            batch = work_units[batch_start:batch_start+batch_size]
            start_time = context.current_utc_datetime
            tasks = [context.call_activity('activity_upload_from_blob', wu) for wu in batch]
            batch_results = yield context.task_all(tasks)
            end_time = context.current_utc_datetime
            duration = (end_time - start_time).total_seconds() or 0.001
            results.extend(batch_results)
            total_requests = sum(r.get('requests_made', 0) for r in batch_results)
            throttle_events = sum(r.get('throttle_events', 0) for r in batch_results)
            reqs_per_min = (total_requests / duration) * 60 if duration > 0 else 0
            if batch_start + batch_size < len(work_units):
                delay = 0
                if reqs_per_min > TARGET_MAX_REQUESTS_PER_MIN:
                    factor = reqs_per_min / TARGET_MAX_REQUESTS_PER_MIN
                    delay = duration * (factor - 1)
                if throttle_events:
                    delay += 2 * throttle_events
                if delay > 0:
                    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=delay))

        total_ind = sum(r.get('indicators_uploaded', 0) for r in results)
        total_req = sum(r.get('requests_made', 0) for r in results)
        total_throttle = sum(r.get('throttle_events', 0) for r in results)

        clean_calls = [context.call_activity('activity_cleanup_blob', {
            'blob_name': s['blob_name'],
            'indicator_type': s['indicator_type'],
            'config': config
        }) for s in sources]
        yield context.task_all(clean_calls)

        return {
            'success': True,
            'work_units': len(work_units),
            'indicators_uploaded': total_ind,
            'requests_made': total_req,
            'throttle_events': total_throttle
        }
    except Exception as e:
        logging.error(f"Orchestrator V3 error: {e}")
        raise


main = df.Orchestrator.create(orchestrator_function_v3)
