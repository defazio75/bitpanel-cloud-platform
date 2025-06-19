print("✅ Hello from bot_runner")

try:
    import controller
    print("✅ controller imported successfully")
except Exception as e:
    print(f"❌ Error importing controller: {e}")
    import traceback
    traceback.print_exc()
