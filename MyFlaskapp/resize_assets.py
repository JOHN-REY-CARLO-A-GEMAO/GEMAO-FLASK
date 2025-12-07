
import os
from PIL import Image

assets_dir = r"c:\Users\Administrator\Downloads\GEMAO-FLASK (1)-20251205T044439Z-3-001\GEMAO-FLASK\MyFlaskapp\games\assets"
backup_dir = os.path.join(assets_dir, "originals")

if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

small_files = [
    'shuriken.png', 'kunai_flying.png', 'fish.png', 'bandage_icon.png',
    'icon_earth.png', 'icon_fire.png', 'icon_lightning.png', 'icon_water.png', 'icon_wind.png',
    'rock.png'
]

medium_files = [
    'akatsuki_member.png', 'naruto_head.png', 'naruto_body.png', 'naruto_run.png',
    'kakashi_portrait.png', 'target.png', 'wood_log.png', 'bush_hiding.png',
    'bijuu_exit.png', 'scroll_secret.png', 'card_back_leaf.png',
    'sign_bird.png', 'sign_boar.png', 'sign_dog.png', 'sign_tiger.png',
    'hand_palm.png', 'rasengan_complete.png',
    'chakra_spin_med.png', 'chakra_spin_small.png',
    'fire.png', 'wind.png', 'earth.png', 'lightning.png'
]

# Ensure we process each file
for filename in os.listdir(assets_dir):
    if filename in small_files:
        target_size = (64, 64)
    elif filename in medium_files:
        target_size = (128, 128)
    else:
        continue # Skip files not in our lists (backgrounds, textures)

    file_path = os.path.join(assets_dir, filename)
    backup_path = os.path.join(backup_dir, filename)
    
    try:
        # Backup first
        if not os.path.exists(backup_path):
            with open(file_path, 'rb') as f_in:
                with open(backup_path, 'wb') as f_out:
                    f_out.write(f_in.read())
        
        # Resize
        with Image.open(file_path) as img:
            # Resize using LANCZOS for quality
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            resized_img.save(file_path)
            print(f"Resized {filename} to {target_size}")
            
    except Exception as e:
        print(f"Failed to resize {filename}: {e}")

print("Resize complete.")
