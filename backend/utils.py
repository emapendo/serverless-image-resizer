from PIL import Image, ImageOps, ImageDraw, ImageFont
import io


def resize_image(image_bytes, max_width=1200, max_height=900, format="JPEG", add_watermark=False):
    """Resize image while maintaining aspect ratio, fix EXIF rotation, and optionally apply watermark."""
    image = Image.open(io.BytesIO(image_bytes))

    # Auto-rotate the image based on EXIF data
    image = ImageOps.exif_transpose(image)

    # Resize while maintaining aspect ratio
    image.thumbnail((max_width, max_height))

    # Apply watermark ONLY if the user selected it
    if add_watermark:
        watermark_text = "CS496"
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 40)  # Use Arial if available
        except IOError:
            font = ImageFont.load_default()  # Fallback to default font

        # Get text bounding box (replaces deprecated textsize())
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Ensure the text is placed within the image bounds
        position = (image.width - text_width - 20, image.height - text_height - 20)  # Bottom-right corner

        # Draw watermark with background for better visibility
        padding = 10
        background_position = (
            position[0] - padding,
            position[1] - padding,
            position[0] + text_width + padding,
            position[1] + text_height + padding
        )

        # Draw a semi-transparent rectangle behind text
        draw.rectangle(background_position, fill=(0, 0, 0, 150))  # Dark background for visibility
        draw.text(position, watermark_text, fill=(255, 255, 255, 255), font=font)  # White text

    # Convert and save image in chosen format
    output = io.BytesIO()
    if format == "PNG":
        image.save(output, format="PNG", optimize=True)
    elif format == "WEBP":
        image.save(output, format="WEBP", quality=90)
    else:
        image.save(output, format="JPEG", quality=95)

    output.seek(0)
    return output
