"""
Ryu SDN Controller REST API client
"""

import requests
import json
from typing import Dict, List, Optional, Callable


class RyuClient:
    """Ryu Controller REST API Client"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.log_callback: Optional[Callable[[str], None]] = None

    def set_log_callback(self, callback: Callable[[str], None]):
        """Set logging callback function"""
        self.log_callback = callback

    def log(self, message: str):
        """Log message through callback"""
        if self.log_callback:
            self.log_callback(message)

    def _log_request(self, method: str, url: str, body: Optional[Dict] = None):
        """Log HTTP request details"""
        self.log(f"[Ryu] ▶ {method} {url}")
        if body:
            self.log(f"[Ryu] ▶ Request Body: {json.dumps(body, indent=2)}")

    def _log_response(self, response: requests.Response):
        """Log HTTP response details"""
        self.log(f"[Ryu] ◀ Status: {response.status_code}")
        try:
            response_json = response.json()
            if response_json:
                self.log(f"[Ryu] ◀ Response Body: {json.dumps(response_json, indent=2)}")
        except:
            if response.text:
                self.log(f"[Ryu] ◀ Response Text: {response.text}")

    def install_flow(
        self, dpid: int, priority: int, match: Dict, actions: List[Dict]
    ) -> bool:
        """Install flow entry"""
        url = f"{self.base_url}/stats/flowentry/add"

        flow = {
            "dpid": dpid,
            "priority": priority,
            "match": match,
            "actions": actions,
        }

        try:
            self._log_request("POST", url, flow)
            response = requests.post(url, json=flow, timeout=5)
            self._log_response(response)

            if response.status_code == 200:
                self.log(f"[Ryu] Flow installed successfully")
                return True
            else:
                self.log(f"[Ryu] Flow installation failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"[Ryu] Error installing flow: {e}")
            return False

    def install_sfc(
        self,
        dpid: int,
        priority: int,
        h1_port: int,
        fw_port: int,
        nat_port: int,
        h2_port: int,
    ) -> bool:
        """
        Install Service Function Chain
        h1 -> fw -> nat -> h2
        """
        flows = []

        # Flow 1: h1 -> fw
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": h1_port},
                "actions": [{"type": "OUTPUT", "port": fw_port}],
            }
        )

        # Flow 2: fw -> nat
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": fw_port},
                "actions": [{"type": "OUTPUT", "port": nat_port}],
            }
        )

        # Flow 3: nat -> h2
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": nat_port},
                "actions": [{"type": "OUTPUT", "port": h2_port}],
            }
        )

        # Flow 4: h2 -> nat (reverse)
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": h2_port},
                "actions": [{"type": "OUTPUT", "port": nat_port}],
            }
        )

        # Flow 5: nat -> fw (reverse)
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": nat_port, "eth_type": 0x0800},  # IP traffic
                "actions": [{"type": "OUTPUT", "port": fw_port}],
            }
        )

        # Flow 6: fw -> h1 (reverse)
        flows.append(
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": fw_port, "eth_type": 0x0800},
                "actions": [{"type": "OUTPUT", "port": h1_port}],
            }
        )

        url = f"{self.base_url}/stats/flowentry/add"
        success_count = 0

        self.log(f"[Ryu] === Installing SFC with {len(flows)} flows ===")

        for i, flow in enumerate(flows, 1):
            try:
                self.log(f"[Ryu] --- Flow {i}/{len(flows)} ---")
                self._log_request("POST", url, flow)
                response = requests.post(url, json=flow, timeout=5)
                self._log_response(response)

                if response.status_code == 200:
                    success_count += 1
                    self.log(f"[Ryu] Flow {i} installed successfully")
                else:
                    self.log(f"[Ryu] Flow {i} failed: {response.status_code}")
            except requests.exceptions.ConnectionError as e:
                self.log(f"[Ryu] 연결 오류: Ryu 컨트롤러가 {self.base_url}에서 실행 중이 아닙니다.")
                self.log(f"[Ryu] 해결 방법: Docker 컨테이너에서 Ryu를 시작하세요:")
                self.log(f"[Ryu]   1. docker-compose up -d")
                self.log(f"[Ryu]   2. docker ps  (컨테이너 이름 확인)")
                self.log(f"[Ryu]   3. docker exec smart-network-sdn bash -c 'nohup ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest --verbose &'")
                break
            except Exception as e:
                self.log(f"[Ryu] Error installing flow {i}: {e}")

        self.log(f"[Ryu] === SFC Installation Complete: {success_count}/{len(flows)} flows installed ===")
        if success_count == 0 and len(flows) > 0:
            self.log(f"[Ryu] SFC 설치 실패")
        elif success_count == len(flows):
            self.log(f"[Ryu] SFC 설치 성공")
        else:
            self.log(f"[Ryu] SFC 부분 설치: {success_count}/{len(flows)}")
        return success_count == len(flows)

    def install_bypass(
        self, dpid: int, priority: int, h1_port: int, h2_port: int
    ) -> bool:
        """
        Install bypass flows (direct h1 <-> h2)
        """
        flows = [
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": h1_port},
                "actions": [{"type": "OUTPUT", "port": h2_port}],
            },
            {
                "dpid": dpid,
                "priority": priority,
                "match": {"in_port": h2_port},
                "actions": [{"type": "OUTPUT", "port": h1_port}],
            },
        ]

        url = f"{self.base_url}/stats/flowentry/add"
        success_count = 0

        self.log(f"[Ryu] === Installing Bypass with {len(flows)} flows ===")

        for i, flow in enumerate(flows, 1):
            try:
                self.log(f"[Ryu] --- Flow {i}/{len(flows)} ---")
                self._log_request("POST", url, flow)
                response = requests.post(url, json=flow, timeout=5)
                self._log_response(response)

                if response.status_code == 200:
                    success_count += 1
                    self.log(f"[Ryu] Bypass flow {i} installed successfully")
                else:
                    self.log(f"[Ryu] Bypass flow {i} failed: {response.status_code}")
            except requests.exceptions.ConnectionError as e:
                self.log(f"[Ryu] 연결 오류: Ryu 컨트롤러가 {self.base_url}에서 실행 중이 아닙니다.")
                self.log(f"[Ryu] 해결 방법: Docker 컨테이너에서 Ryu를 시작하세요:")
                self.log(f"[Ryu]   1. docker-compose up -d")
                self.log(f"[Ryu]   2. docker ps  (컨테이너 이름 확인)")
                self.log(f"[Ryu]   3. docker exec smart-network-sdn bash -c 'nohup ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest --verbose &'")
                break  # No point trying other flows if connection is down
            except Exception as e:
                self.log(f"[Ryu] Error installing bypass flow {i}: {e}")

        self.log(f"[Ryu] === Bypass Installation Complete: {success_count}/{len(flows)} flows installed ===")
        if success_count == 0 and len(flows) > 0:
            self.log(f"[Ryu] Bypass 설치 실패")
        elif success_count == len(flows):
            self.log(f"[Ryu] Bypass 설치 성공")
        else:
            self.log(f"[Ryu] Bypass 부분 설치: {success_count}/{len(flows)}")
        return success_count == len(flows)

    def dump_flows(self, dpid: int) -> Optional[List[Dict]]:
        """Dump all flows for a datapath"""
        url = f"{self.base_url}/stats/flow/{dpid}"

        try:
            self._log_request("GET", url)
            response = requests.get(url, timeout=5)
            self._log_response(response)

            if response.status_code == 200:
                flows = response.json()
                flow_list = flows.get(str(dpid), [])
                self.log(f"[Ryu] Retrieved {len(flow_list)} flows for DPID {dpid}")
                return flow_list
            else:
                self.log(f"[Ryu] Failed to retrieve flows: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError as e:
            self.log(f"[Ryu] 연결 오류: Ryu 컨트롤러가 {self.base_url}에서 실행 중이 아닙니다.")
            self.log(f"[Ryu] Docker 컨테이너에서 Ryu를 시작하세요.")
            return None
        except Exception as e:
            self.log(f"[Ryu] Error retrieving flows: {e}")
            return None

    def clear_flows(self, dpid: int) -> bool:
        """Clear all flows for a datapath"""
        url = f"{self.base_url}/stats/flowentry/clear/{dpid}"

        try:
            self._log_request("DELETE", url)
            response = requests.delete(url, timeout=5)
            self._log_response(response)

            if response.status_code == 200:
                self.log(f"[Ryu] Flows cleared for DPID {dpid}")
                return True
            else:
                self.log(f"[Ryu] Failed to clear flows: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            self.log(f"[Ryu] 연결 오류: Ryu 컨트롤러가 {self.base_url}에서 실행 중이 아닙니다.")
            self.log(f"[Ryu] Docker 컨테이너에서 Ryu를 시작하세요.")
            return False
        except Exception as e:
            self.log(f"[Ryu] Error clearing flows: {e}")
            return False

    def get_switches(self) -> Optional[List[int]]:
        """Get list of connected switches"""
        url = f"{self.base_url}/stats/switches"

        try:
            self._log_request("GET", url)
            response = requests.get(url, timeout=5)
            self._log_response(response)

            if response.status_code == 200:
                switches = response.json()
                self.log(f"[Ryu] Found {len(switches)} switches")
                return switches
            else:
                self.log(f"[Ryu] Failed to get switches: {response.status_code}")
                return None
        except Exception as e:
            self.log(f"[Ryu] Error getting switches: {e}")
            return None
