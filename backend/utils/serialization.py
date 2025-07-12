
def ensure_serializable(obj):
    """Đảm bảo đối tượng có thể serialize thành JSON."""
    if isinstance(obj, dict):
        return {k: ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif hasattr(obj, '__dict__'):
        return ensure_serializable(obj.__dict__)
    else:
        return str(obj)  # Chuyển đổi các đối tượng không serializable thành string