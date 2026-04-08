// Sidecar for spawning and managing the Python FastAPI backend

use std::process::{Child, Command};
use std::path::PathBuf;
use std::env;

#[tauri::command]
fn start_backend() -> Result<String, String> {
    // Get the path to the Python backend
    let mut backend_path = env::current_exe().unwrap_or_else(|| "auto-applier".into());
    backend_path.pop(); // Remove binary name
    backend_path.push("backend");
    backend_path.push("auto_applier_api");

    println!("Starting Python backend at: {:?}", backend_path);

    // TODO: Implement actual Python backend spawning
    // This should:
    // 1. Spawn Python subprocess with: python -m auto_applier_api
    // 2. Read stdout to get the assigned port
    // 3. Keep process reference for monitoring and shutdown
    // 4. Return port to frontend via command response

    Ok("Backend started on port 8000".to_string())
}

#[tauri::command]
fn stop_backend() -> Result<String, String> {
    println!("Stopping Python backend...");

    // TODO: Implement actual backend shutdown
    // This should:
    // 1. Send SIGTERM to Python process
    // 2. Wait for graceful shutdown
    // 3. Clean up any PID file

    Ok("Backend stopped".to_string())
}

#[tauri::command]
async fn get_backend_status() -> Result<String, String> {
    println!("Checking backend status...");

    // TODO: Implement actual backend status check
    // This should:
    // 1. Check if Python process is running
    // 2. Check if it's responsive via HTTP
    // 3. Return status: running, stopped, or crashed

    Ok("Backend status: running".to_string())
}
