from main_logic.main_robot import run_main_robot

def send_robot_command(product_code):
    print(f"[Robot] 📦 สั่งงานหุ่นยนต์สำหรับสินค้า: {product_code}")
    run_main_robot("shelf_marker", product_code)
    return f"Robot command sent for product {product_code}"