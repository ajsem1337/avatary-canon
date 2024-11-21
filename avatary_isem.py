from PIL import Image, ImageDraw, ImageFont
import random
import os
import argparse

# Function to create an avatar
def create_avatar(text, size=(256, 256)):
    # Random color for the background
    bg_color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))

    # Create a blank image
    img = Image.new('RGB', size, color=bg_color)

    # Add text to the image
    draw = ImageDraw.Draw(img)
    font_size = 100
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

    # Get text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Calculate text position (centered)
    text_x = (size[0] - text_width) / 2
    text_y = (size[1] - text_height) / 2 - 10  # Adjust vertical position slightly

    # Apply text to the image
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

    return img

# Main script
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate an avatar with initials.")
    parser.add_argument("--user", type=str, help="Specify initials for the avatar")
    args = parser.parse_args()

    # Directory to save avatars
    save_directory = "./avatary/"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    if args.user:
        # Base filename
        base_filename = f"etg_{args.user}.png"
        avatar_path = os.path.join(save_directory, base_filename)
        counter = 1

        # Check if file exists and adjust filename if necessary
        while os.path.exists(avatar_path):
            avatar_path = os.path.join(save_directory, f"etg_{args.user}_{counter}.png")
            counter += 1

        # Generate and save avatar
        avatar = create_avatar(args.user)
        avatar.save(avatar_path)
        print(f"Avatar created for user '{args.user}' at '{avatar_path}'")
    else:
        # Display a warning if no initials were provided
        print("Warning: Please specify initials using the --user argument. Example: python tworzenie_avatarów.py --user Kw")

if __name__ == "__main__":
    main()
