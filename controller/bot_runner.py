print("✅ Hello from bot_runner")

print("👣 STEP 1: Trying to import controller...")

try:
    import controller
    print("✅ STEP 2: Controller imported successfully")
except Exception as e:
    print(f"❌ STEP 2: Failed to import controller: {e}")
    import traceback
    traceback.print_exc()

try:
    print("🚀 Starting controller loop...")
    controller.run_controller()
except Exception as e:
    print(f"❌ Error running controller: {e}")
    import traceback
    traceback.print_exc()
