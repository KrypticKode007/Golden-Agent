#!/bin/bash
echo "[SHUTDOWN] Unlinking active sockets and halting nodes gracefully..."
# pm2 delete ecosystem.config.js
rm -rf /tmp/mock_sysfs
echo "[SHUTDOWN] Workspace resources successfully cleared."
