"""
Lumen Threat Intelligence Connector - Orchestrator Function (Chunked Version)

This function coordinates the parallel processing of threat intelligence data
by managing multiple activity functions that upload STIX objects to Microsoft Sentinel.

Key Features:
- Processes multiple chunked blobs in parallel to maximize throughput
- Stays within API rate limits (95 requests/minute)
- Handles large datasets efficiently through blob storage references
- Automatically cleans up all chunk blobs after completion

"""

import logging
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to manage parallel chunk uploads from blob storage.
    
    This function coordinates the processing of threat intelligence data by:
    1. Reading a list of blob storage references from input (pre-chunked blobs)
    2. Creating parallel activity function calls for each chunk/blob
    3. Managing rate limits by processing in groups
    4. Cleaning up all blobs after successful completion
    
    Args:
        context (df.DurableOrchestrationContext): Durable Functions context containing:
            - blob_container: Name of the blob container
            - blob_names: List of blob file names (each a chunk of threat data)
            - config: Configuration dictionary with API credentials
            - parallel_chunk_size: Number of blobs to process in parallel (optional)
    
    Returns:
        list: List of results from all chunk processing activities
    """
    try:
        # Extract input parameters from the starter function
        input_data = context.get_input()
        blob_container = input_data['blob_container']
        blob_names = input_data['blob_names']  # List of chunked blob names
        config = input_data['config']
        parallel_chunk_size = input_data.get('parallel_chunk_size', 2)

        results = []
        total_chunks = len(blob_names)
        chunk_index = 0

        logging.info(f"Starting chunked orchestration for {total_chunks} blobs in container: {blob_container}")
        logging.info(f"Parallel chunk size: {parallel_chunk_size}")

        # Main processing loop: process all blobs in parallel groups
        while chunk_index < total_chunks:
            chunk_group = blob_names[chunk_index:chunk_index+parallel_chunk_size]
            parallel_tasks = []
            for blob_name in chunk_group:
                parallel_tasks.append(
                    context.call_activity('activity_upload_batch', {
                        'blob_container': blob_container,
                        'blob_name': blob_name,
                        'config': config
                    })
                )
            group_results = yield context.task_all(parallel_tasks)
            results.extend(group_results)
            chunk_index += parallel_chunk_size            # Progress logging - only log at meaningful intervals (every 20% or every 100 chunks)
            chunks_done = len(results)
            log_interval = min(100, max(1, total_chunks // 5))  # Log every 20% or every 100 chunks
            
            if chunks_done % log_interval == 0 or chunks_done == total_chunks:
                progress_pct = (chunks_done / total_chunks) * 100
                logging.info(f"Progress: {chunks_done}/{total_chunks} chunks ({progress_pct:.1f}%)")

        logging.info(f"Orchestration completed. Processed {len(results)} chunks total")        # Clean up all chunk blobs after successful processing (optimized batching)
        logging.info(f"Cleaning up {len(blob_names)} temporary blobs in optimized batches...")
        
        # Calculate optimal batch size (aim for ~2-3 minutes per batch to stay well under 10min limit)
        # Based on testing: ~75 blobs per batch is optimal for Azure Storage delete performance
        optimal_batch_size = 75  # Sweet spot for performance vs timeout
        cleanup_tasks = []
        
        for i in range(0, len(blob_names), optimal_batch_size):
            batch = blob_names[i:i+optimal_batch_size]
            cleanup_tasks.append(
                context.call_activity('activity_cleanup_blobs_batch', {
                    'blob_container': blob_container,
                    'blob_names': batch
                })
            )
        
        logging.info(f"Created {len(cleanup_tasks)} cleanup batch tasks")
        
        # Execute cleanup batches in parallel (each batch handles ~75 blobs internally in parallel)
        cleanup_results = yield context.task_all(cleanup_tasks)
        
        # Summarize results
        total_deleted = sum(r['deleted'] for r in cleanup_results)
        total_failed = sum(r['failed'] for r in cleanup_results)
        max_execution_time = max(r['execution_time'] for r in cleanup_results) if cleanup_results else 0
        
        logging.info(f"Blob cleanup complete: {total_deleted} deleted, {total_failed} failed in {max_execution_time:.2f}s max")

        return results

    except Exception as e:
        logging.error(f"Orchestrator error: {e}")
        raise

# Create the orchestrator function binding
main = df.Orchestrator.create(orchestrator_function)
