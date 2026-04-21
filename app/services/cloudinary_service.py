import cloudinary.uploader

async def upload_avatar(file, user_id):
    result = cloudinary.uploader.upload(
        file.file,
        public_id=f"user_{user_id}",
        overwrite=True,
        transformation={"width": 250, "height": 250, "crop": "fill"}
    )
    return result["secure_url"]