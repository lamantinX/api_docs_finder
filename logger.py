"""Progress logging module for API documentation finder."""

from tqdm import tqdm


class ProgressLogger:
    """Logger with progress bar for tracking API method processing."""
    
    def __init__(self, total_methods: int):
        """
        Initialize progress logger with tqdm progress bar.
        
        Args:
            total_methods: Total number of API methods to process
        """
        self.pbar = tqdm(total=total_methods, desc="Processing API methods")
    
    def log_success(self, name: str, method: str):
        """
        Log successful processing of an API method.
        
        Args:
            name: API name (e.g., "bitrix24")
            method: Method name (e.g., "add user")
        """
        self.pbar.write(f"✅ найдено для {name} {method}")
    
    def log_error(self, name: str, method: str, error: str):
        """
        Log error during processing of an API method.
        
        Args:
            name: API name (e.g., "bitrix24")
            method: Method name (e.g., "add user")
            error: Error message
        """
        self.pbar.write(f"❌ ошибка для {name} {method}: {error}")
    
    def update(self):
        """Increment progress bar by one step."""
        self.pbar.update(1)
    
    def close(self):
        """Finalize and close the progress bar."""
        self.pbar.close()
