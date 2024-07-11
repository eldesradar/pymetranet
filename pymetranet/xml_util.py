#!/bin/env python

import xml.etree.ElementTree as ET

class XmlUtil:
    class INFO_SERVO_CMD:
        def __init__(self):
            self.mode: str = ""
            self.elevation: str = ""
            self.start_az: str = ""
            self.end_az: str = ""
            self.az_rate: str = ""
            self.angle_width: str = ""
            self.min_elevation: str = ""
            self.max_elevation: str = ""

    class INFO_RSP_CMD:
        def __init__(self):
            self.mode: str = ""
            self.rcr: str = ""
            self.pol: str = ""
            self.prf: str = ""
            self.dprf: str = ""
            self.rng: str = ""
            self.npl: str = ""
            self.asyc: str = ""
            self.cf: str = ""
            self.sqi: str = ""
            self.csr: str = ""
            self.log: str = ""
            self.exe: str = ""

    class INFO_TX_CMD:
        def __init__(self):
            self.bt: str = ""
            self.at: str = ""
            self.rad: str = ""
            self.pot: str = ""

    class SWEEP:
        def __init__(self):
            self.ID: str = ""
            self.servo_cmd: INFO_SERVO_CMD = INFO_SERVO_CMD()
            self.rsp_cmd: INFO_RSP_CMD = INFO_RSP_CMD()
            self.tx_cmd: INFO_TX_CMD = INFO_TX_CMD()
        
    @staticmethod
    def parse_sweep_data(self, xml_data: str) -> SWEEP:
        sweep_data = SWEEP()
        root = ET.fromstring(xml_data)

        sweep_node = root.find("SWEEP_DATA")
        if sweep_node is not None:
            servo_node = sweep_node.find("SERVO")
            if servo_node is not None:
                cmd_node = servo_node.find("cmd")
                if cmd_node is not None:
                    sweep_data.servo_cmd = INFO_SERVO_CMD(
                        mode=cmd_node.get("mode", ""),
                        elevation=cmd_node.get("elevation", ""),
                        start_az=cmd_node.get("start_az", ""),
                        end_az=cmd_node.get("end_az", ""),
                        az_rate=cmd_node.get("az_rate", ""),
                        angle_width=cmd_node.get("angle_width", ""),
                        min_elevation=cmd_node.get("min_elevation", ""),
                        max_elevation=cmd_node.get("max_elevation", "")
                    )

            rsp_node = sweep_node.find("RSP")
            if rsp_node is not None:
                cmd_node = rsp_node.find("cmd")
                if cmd_node is not None:
                    sweep_data.rsp_cmd = INFO_RSP_CMD(
                        mode=cmd_node.get("mode", ""),
                        rcr=cmd_node.get("rcr", ""),
                        pol=cmd_node.get("pol", ""),
                        prf=cmd_node.get("prf", ""),
                        dprf=cmd_node.get("dprf", ""),
                        rng=cmd_node.get("rng", ""),
                        npl=cmd_node.get("npl", ""),
                        asyc=cmd_node.get("asyc", ""),
                        cf=cmd_node.get("cf", ""),
                        sqi=cmd_node.get("sqi", ""),
                        csr=cmd_node.get("csr", ""),
                        log=cmd_node.get("log", ""),
                        exe=cmd_node.get("exe", "")
                    )

            tx_node = sweep_node.find("TX")
            if tx_node is not None:
                cmd_node = tx_node.find("cmd")
                if cmd_node is not None:
                    sweep_data.tx_cmd = INFO_TX_CMD(
                        bt=cmd_node.get("BT", ""),
                        at=cmd_node.get("AT", ""),
                        rad=cmd_node.get("RAD", ""),
                        pot=cmd_node.get("POT", "")
                    )

        return sweep_data