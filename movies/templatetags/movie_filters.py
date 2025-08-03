from django import template

register = template.Library()

@register.filter
def star_character(value, star_position):
    """
    Return the appropriate star character based on the rating.
    star_position: 1-5 (which star we're rendering)
    value: the 10-point rating (e.g., 6.2)
    Returns: tuple of (star_char, css_class)
    """
    if value is None:
        return ("★", "text-slate-600")
    
    try:
        rating = float(value)
        star_pos = int(star_position)
        
        # Convert 10-point rating to 5-point scale
        five_star_rating = (rating * 5) / 10
        
        # Full star
        if five_star_rating >= star_pos:
            return ("★", "text-yellow-400")
        # Half star (within 0.5 of the star position)
        elif five_star_rating >= star_pos - 0.5:
            return ("☆", "text-yellow-400")  # Using empty star with yellow color for half-star effect
        # Empty star
        else:
            return ("☆", "text-slate-600")
    except (ValueError, TypeError):
        return ("☆", "text-slate-600")

@register.filter
def star_class(value, star_position):
    """
    Return the appropriate CSS class for a star based on the rating.
    star_position: 1-5 (which star we're rendering)
    value: the 10-point rating (e.g., 6.2)
    """
    if value is None:
        return "text-slate-600"
    
    try:
        rating = float(value)
        star_pos = int(star_position)
        
        # Convert 10-point rating to 5-point scale
        five_star_rating = (rating * 5) / 10
        
        # Full star
        if five_star_rating >= star_pos:
            return "text-yellow-400"
        # Half star (within 0.5 of the star position)
        elif five_star_rating >= star_pos - 0.5:
            return "text-yellow-400 half-star"
        # Empty star
        else:
            return "text-slate-600"
    except (ValueError, TypeError):
        return "text-slate-600" 