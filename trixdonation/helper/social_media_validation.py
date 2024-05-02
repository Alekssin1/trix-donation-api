import re


def is_valid_social_media_url(url, social_media):
    match social_media:
        case "twitter":
            pattern = r'^https?://(?:www\.)?(?:twitter\.com|x\.com)/[\w-]+$'
        case "facebook":
            pattern = r'^https?://www\.facebook\.com/[\w.-]+(?:/\?locale=[a-zA-Z_]+)?/$'
        case "instagram":
            pattern = r'^https?://www\.instagram\.com/[\w.-]+/$'
        case _:
            return False 

    if re.match(pattern, url):
        return True
    else:
        return False