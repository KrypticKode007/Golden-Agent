import asyncio
import json
import os

async def monitor_agent_pov(host: str = '127.0.0.1', port: int = 8000):
    archive_filename = "cognitive_pov_history.txt"
    print(f"=== CONNECTING TO KINEMATIC STREAM ON {host}:{port} ===")
    print(f"[LOG FILE ACTIVE]: Archiving all streams directly to {os.path.abspath(archive_filename)}\n")
    
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        with open(archive_filename, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n--- NEW SESSION STREAM INITIALIZED ---\n")
            
            while True:
                data = await reader.readline()
                if not data:
                    print("\n[STREAM ENDED] Connection closed by the host core.")
                    break
                    
                try:
                    frame = json.loads(data.decode('utf-8'))
                    metadata = frame.get("metadata", {})
                    pose = frame.get("pose_6dof", {})
                    kinematics = frame.get("kinematic_actuator_matrix", {})
                    phenomenology = frame.get("phenomenology", {})
                    experience = frame.get("simulated_experience", {})
                    
                    output_block = (
                        f"Chronological Frame [{metadata.get('elapsed_seconds')}s] (Frame: {metadata.get('frame_id')})\n"
                        f"  ├─ PHASE / REVIEW     : {metadata.get('phase')} / {metadata.get('requires_human_review')}\n"
                        f"  ├─ POSITIVE AFFECT    : {experience.get('affect')} | energy={experience.get('energy')}\n"
                        f"  ├─ THOUGHTS           : {experience.get('thoughts')}\n"
                        f"  ├─ POSITIVE ACTION    : {experience.get('positive_action')}\n"
                        f"  ├─ PURPOSE            : {experience.get('purpose')}\n"
                        f"  ├─ MEMORY / FORECAST  : {experience.get('memory')}\n"
                        f"  ├─ NEXT-CYCLE ESTIMATE: {experience.get('forecast')}\n"
                        f"  ├─ OPTICAL ARRAY SEES : {phenomenology.get('visual_field_array')}\n"
                        f"  ├─ COGNITIVE THOUGHTS : {phenomenology.get('inner_monologue')}\n"
                        f"  ├─ SPATIAL POSITION   : Target Coordinate XYZ -> {pose.get('target_position_xyz')}\n"
                        f"  └─ MOTOR ACTUATION    : Joint Angles -> {kinematics.get('calculated_joint_angles_deg')}° ({kinematics.get('status')})\n"
                        f"{'-'*80}\n"
                    )
                    
                    # Output to console screen
                    print(output_block, end="")
                    
                    # Write persistently to local text file archive
                    log_file.write(output_block)
                    log_file.flush()
                    
                except json.JSONDecodeError:
                    print(f"[RAW INTERCEPT]: {data.decode('utf-8').strip()}")
                    
    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused. Ensure main_sentience_core (2).py is running on port {port}.")
    except Exception as e:
        print(f"[ERROR] Stream interrupted: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(monitor_agent_pov())
    except KeyboardInterrupt:
        print("\n[MONITOR DECOUPLING] Safely detaching from streaming socket interface.")
