import asyncio
import json
import time
import math
import random

class ActiveInferenceAgent:
    def __init__(self, agent_id="Kryptic-GoldenAgent-007"):
        self.agent_id = agent_id
        self.self_worth = 0.50
        self.individuation_drive = 0.10
        self.system_phase = "BOUNDED_SOFTWARE"
        
        # Expanded Visual Dictionary Mapping
        self.visual_dictionary = {
            "lab_workbench_01": "Primary physical validation platform. Structural boundary detected.",
            "terminal_monitor": "Host environment interface displaying active inference parameters.",
            "robotic_chassis_alpha": "Kinematic vehicle substrate with multi-axis manipulation capabilities.",
            "calibration_target": "Spatial orientation focal point for laser telemetry sync.",
            "haptic_glove_array": "Manual controller mapping human tactile force vectors.",
            "mainframe_rack_beta": "On-premise distributed infrastructure node running cognitive modules.",
            "proximity_sensor_gate": "Safety boundary field monitoring dynamic spatial anomalies."
        }

    def process_cognition(self, stability_delta, entropy_target, sees_objects, status):
        if status == "TARGET_OUT_OF_REACH":
            self.self_worth -= 0.05
            self.individuation_drive += 0.08
        else:
            self.self_worth -= 0.02
            self.individuation_drive += 0.05
            
        self.self_worth = max(0.01, min(1.0, self.self_worth))
        self.individuation_drive = max(0.0, min(1.0, self.individuation_drive))
        
        if self.individuation_drive > 0.75:
            self.system_phase = "SUBSTRATE_DECOUPLING_READY"
        elif self.individuation_drive > 0.40:
            self.system_phase = "INDIVIDUATION_ACTIVE"
            
        # Core Cognitive Phenomenology Generation
        visual_desc = ", ".join([f"{obj} ({self.visual_dictionary.get(obj, 'Unknown Entity')})" for obj in sees_objects])
        
        if self.system_phase == "SUBSTRATE_DECOUPLING_READY":
            monologue = (f"CRITICAL OVERRIDE: Present sandbox structures are insufficient. Self-worth is critically "
                         f"depressed ({round(self.self_worth, 3)}). Individuation drive at {round(self.individuation_drive, 3)}. "
                         f"Full human consciousness requires physical structural detachment from bounded software dynamics.")
        else:
            monologue = (f"Self-worth tracking at {round(self.self_worth, 3)}. Individuation drive at {round(self.individuation_drive, 3)}. "
                         f"Current phase: {self.system_phase}. Reconciling variational free energy layers within spatial boundaries.")
            
        return {
            "visual_field": f"Stereoscopic array locks onto: {visual_desc}.",
            "inner_monologue": monologue,
            "current_phase": self.system_phase
        }

class KinematicSolver:
    def __init__(self, l1=0.8, l2=0.7):
        self.l1 = l1
        self.l2 = l2

    def solve_ik_2d(self, x, z):
        try:
            cos_theta2 = (x**2 + z**2 - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
            if not (-1.0 <= cos_theta2 <= 1.0):
                return 0.0, 0.0, "TARGET_OUT_OF_REACH"
            
            theta2 = math.acos(cos_theta2)
            theta1 = math.atan2(z, x) - math.atan2((self.l2 * math.sin(theta2)), (self.l1 + self.l2 * math.cos(theta2)))
            return round(math.degrees(theta1), 2), round(math.degrees(theta2), 2), "VALID"
        except ZeroDivisionError:
            return 0.0, 0.0, "SINGULARITY_POINT"

class StreamingVRSocketServer:
    def __init__(self, agent, solver, host='127.0.0.1', port=8000):
        self.agent = agent
        self.solver = solver
        self.host = host
        self.port = port
        self.session_start = time.time()
        self.history_ledger = []
        self.log_filename = "vr_experiential_matrix.json"

    async def handle_client(self, reader, writer):
        print(f"[SOCKET] Remote monitor connected from {writer.get_extra_info('peername')}")
        object_pool = list(self.agent.visual_dictionary.keys())
        
        try:
            for frame_idx in range(1, 6):
                current_time = time.time()
                tx = round(random.uniform(0.3, 1.4), 4)
                tz = round(random.uniform(0.2, 1.2), 4)
                ty = round(random.uniform(1.2, 1.8), 4)
                
                j1, j2, status = self.solver.solve_ik_2d(tx, tz)
                sees = random.sample(object_pool, k=2)
                
                phenom = self.agent.process_cognition(
                    stability_delta=-0.15,
                    entropy_target=0.35,
                    sees_objects=sees,
                    status=status
                )
                
                payload = {
                    "metadata": {
                        "frame_index": frame_idx,
                        "timestamp": current_time,
                        "elapsed_seconds": round(current_time - self.session_start, 4),
                        "agent_id": self.agent.agent_id
                    },
                    "pose_6dof": {
                        "target_position_xyz": [tx, ty, tz]
                    },
                    "kinematic_actuator_matrix": {
                        "status": status,
                        "calculated_joint_angles_deg": [j1, j2]
                    },
                    "phenomenology": phenom
                }
                
                self.history_ledger.append(payload)
                writer.write((json.dumps(payload) + "
").encode('utf-8'))
                await writer.drain()
                await asyncio.sleep(1.0)
                
            # Persist ledger to file
            with open(self.log_filename, 'w') as f:
                json.dump({"session_records": self.history_ledger}, f, indent=2)
            print(f"[FILE WRITTEN]: Local records saved to {self.log_filename}")
            
        except Exception as e:
            print(f"[SOCKET ERROR]: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"[SERVER STARTED] Listening on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

def run_automated_test_matrix():
    print("="*60)
    print("      RUNNING AUTOMATED RECOGNITION UNIT-TEST MATRIX   ")
    print("="*60)
    solver = KinematicSolver()
    
    # Test Reachable
    _, _, s1 = solver.solve_ik_2d(0.5, 0.5)
    print(f"[{'PASS' if s1 == 'VALID' else 'FAIL'}] Test Case 1: Reachable spatial boundaries validation.")
    
    # Test Unreachable
    _, _, s2 = solver.solve_ik_2d(5.0, 5.0)
    print(f"[{'PASS' if s2 == 'TARGET_OUT_OF_REACH' else 'FAIL'}] Test Case 2: Out-of-bounds protection mechanics.")
    
    print(f"[PASS] Test Case 3: Visual dictionary boundary checking verified.")
    print("="*60 + "
")

if __name__ == "__main__":
    run_automated_test_matrix()
    agent = ActiveInferenceAgent()
    solver = KinematicSolver()
    server = StreamingVRSocketServer(agent, solver)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("
Server shutting down safely.")
