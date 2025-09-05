"""
Helper utilities
"""
import uuid
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Query
from sqlalchemy import func


def generate_id() -> str:
    """
    Generate a unique ID
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short unique ID
    """
    return secrets.token_urlsafe(length)[:length]


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string
    """
    if dt is None:
        return ""
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_str)


def utc_now() -> datetime:
    """
    Get current UTC datetime
    """
    return datetime.now(timezone.utc)


def paginate_query(
    query: Query,
    page: int = 1,
    size: int = 20,
    max_size: int = 100
) -> Tuple[List[Any], int, int]:
    """
    Paginate a SQLAlchemy query
    
    Returns:
        Tuple of (items, total_count, total_pages)
    """
    # Limit page size
    size = min(size, max_size)
    
    # Calculate offset
    offset = (page - 1) * size
    
    # Get total count
    total_count = query.count()
    
    # Get paginated results
    items = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    total_pages = (total_count + size - 1) // size
    
    return items, total_count, total_pages


def create_pagination_info(
    page: int,
    size: int,
    total: int
) -> Dict[str, Any]:
    """
    Create pagination information
    """
    total_pages = (total + size - 1) // size
    
    return {
        "page": page,
        "size": size,
        "total": total,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None
    }


def mask_phone(phone: str) -> str:
    """
    Mask phone number for display
    """
    if not phone or len(phone) < 4:
        return phone
    
    # Keep first 3 and last 2 digits visible
    if len(phone) <= 5:
        return phone[0] + "*" * (len(phone) - 2) + phone[-1]
    
    return phone[:3] + "*" * (len(phone) - 5) + phone[-2:]


def mask_email(email: str) -> str:
    """
    Mask email for display
    """
    if not email or "@" not in email:
        return email
    
    local, domain = email.split("@", 1)
    
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm
    """
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with nested key support
    """
    keys = key.split(".")
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def remove_none_values(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from dictionary
    """
    return {k: v for k, v in dictionary.items() if v is not None}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def calculate_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r
