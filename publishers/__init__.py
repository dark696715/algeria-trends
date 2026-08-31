"""سجلّ الناشرين المتاحين."""
from . import telegram, facebook, instagram, tiktok

# ترتيب النشر: نبدأ بتيليغرام (الأسهل والأضمن)
ALL = {
    "telegram": telegram,
    "facebook": facebook,
    "instagram": instagram,
    "tiktok": tiktok,
}
