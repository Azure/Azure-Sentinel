import logging
import os


def main(params: dict) -> dict:
    """
    Durable Functions activity to clean up temporary files after processing.
    
    Args:
        params (dict): Activity input parameters containing:
            - file_path (str): Path to temp file to delete
            - indicator_type (str): Type of indicators (for logging)
    
    Returns:
        dict: Cleanup result containing:
            - success (bool): Whether cleanup was successful
            - file_path (str): Path that was cleaned up
            - error (str, optional): Error message if cleanup failed
    """
    file_path = params["file_path"]
    indicator_type = params.get("indicator_type", "unknown")

    try:
        if os.path.exists(file_path):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            os.unlink(file_path)
            logging.info(f"Cleaned up temp file for {indicator_type}: {file_path} ({file_size_mb:.2f} MB)")
            return {
                "success": True,
                "file_path": file_path,
                "indicator_type": indicator_type
            }
        else:
            logging.warning(f"Temp file not found for cleanup: {file_path}")
            return {
                "success": True,  # Not an error if file doesn't exist
                "file_path": file_path,
                "indicator_type": indicator_type,
                "warning": "File not found"
            }

    except Exception as e:
        logging.error(f"Failed to cleanup temp file {file_path}: {e}")
        return {
            "success": False,
            "file_path": file_path,
            "indicator_type": indicator_type,
            "error": str(e)
        }
