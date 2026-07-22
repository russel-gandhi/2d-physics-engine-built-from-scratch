"""Battle analytics module extracting post-match diagnostics and weakness detection from recorded replays."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any
import numpy as np

from replay.recorder import MatchRecorder


@dataclass
class BattleReport:
    """Post-battle diagnostics report containing damage, mobility, and weakness flags."""

    robot_a_name: str
    robot_b_name: str
    winner: str | None
    win_reason: str
    damage_dealt_a: float
    damage_dealt_b: float
    damage_pct_a: float
    damage_pct_b: float
    distance_covered_a: float
    distance_covered_b: float
    successful_attacks_a: int
    successful_attacks_b: int
    weaknesses_a: list[str] = field(default_factory=list)
    weaknesses_b: list[str] = field(default_factory=list)

    def summary_text(self) -> str:
        """Format human-readable post-match battle report."""
        lines = [
            f"=== BATTLE ANALYTICS REPORT ===",
            f"Match Result: Winner = {self.winner} (Reason: {self.win_reason})",
            f"Robot A ({self.robot_a_name}):",
            f"  - Damage Dealt: {self.damage_dealt_a:.1f} HP ({self.damage_pct_a:.1f}% of opponent HP)",
            f"  - Distance Covered: {self.distance_covered_a:.2f} m",
            f"  - Successful Attack Contacts: {self.successful_attacks_a}",
            f"  - Flagged Weaknesses: {', '.join(self.weaknesses_a) if self.weaknesses_a else 'None'}",
            f"Robot B ({self.robot_b_name}):",
            f"  - Damage Dealt: {self.damage_dealt_b:.1f} HP ({self.damage_pct_b:.1f}% of opponent HP)",
            f"  - Distance Covered: {self.distance_covered_b:.2f} m",
            f"  - Successful Attack Contacts: {self.successful_attacks_b}",
            f"  - Flagged Weaknesses: {', '.join(self.weaknesses_b) if self.weaknesses_b else 'None'}",
        ]
        return "\n".join(lines)


def generate_battle_report(replay_data_or_path: dict[str, Any] | str) -> BattleReport:
    """Analyze replay recording payload and generate BattleReport metrics and weakness diagnostics."""
    if isinstance(replay_data_or_path, str):
        data = MatchRecorder.load(replay_data_or_path)
    else:
        data = replay_data_or_path

    metadata = data["metadata"]
    frames = data["frames"]

    r_a_name = metadata.get("robot_a", "Robot A")
    r_b_name = metadata.get("robot_b", "Robot B")
    winner = metadata.get("winner")
    win_reason = metadata.get("win_reason", "unknown")

    if not frames:
        return BattleReport(
            robot_a_name=r_a_name,
            robot_b_name=r_b_name,
            winner=winner,
            win_reason=win_reason,
            damage_dealt_a=0.0,
            damage_dealt_b=0.0,
            damage_pct_a=0.0,
            damage_pct_b=0.0,
            distance_covered_a=0.0,
            distance_covered_b=0.0,
            successful_attacks_a=0,
            successful_attacks_b=0,
        )

    # Initial Durability
    initial_dur_a = frames[0]["robot_a"]["total_durability"]
    initial_dur_b = frames[0]["robot_b"]["total_durability"]

    final_dur_a = frames[-1]["robot_a"]["total_durability"]
    final_dur_b = frames[-1]["robot_b"]["total_durability"]

    # Damage Dealt
    dmg_dealt_a = max(0.0, initial_dur_b - final_dur_b)
    dmg_dealt_b = max(0.0, initial_dur_a - final_dur_a)

    dmg_pct_a = (dmg_dealt_a / max(1.0, initial_dur_b)) * 100.0
    dmg_pct_b = (dmg_dealt_b / max(1.0, initial_dur_a)) * 100.0

    # Distance Covered & Pose Analysis
    pos_a = [np.array(f["robot_a"]["bodies"]["torso"]["pos"]) for f in frames]
    pos_b = [np.array(f["robot_b"]["bodies"]["torso"]["pos"]) for f in frames]

    dist_a = float(sum(np.linalg.norm(pos_a[i] - pos_a[i - 1]) for i in range(1, len(pos_a))))
    dist_b = float(sum(np.linalg.norm(pos_b[i] - pos_b[i - 1]) for i in range(1, len(pos_b))))

    # Attack Contacts & Damage Events
    attacks_a = 0
    attacks_b = 0
    for frame in frames:
        for evt in frame.get("damage_events", []):
            if evt.get("attacker") == "robot_a":
                attacks_a += 1
            elif evt.get("attacker") == "robot_b":
                attacks_b += 1

    # Weakness Heuristics Detection
    weaknesses_a = []
    weaknesses_b = []

    # 1. Low Mobility: average step displacement < 0.01m
    if (dist_a / max(1, len(frames))) < 0.01:
        weaknesses_a.append("low_mobility")
    if (dist_b / max(1, len(frames))) < 0.01:
        weaknesses_b.append("low_mobility")

    # 2. Slow Recovery / Knockdown Duration
    tilted_frames_a = sum(1 for f in frames if abs(f["robot_a"]["bodies"]["torso"]["angle"]) > 1.0)
    tilted_frames_b = sum(1 for f in frames if abs(f["robot_b"]["bodies"]["torso"]["angle"]) > 1.0)

    if tilted_frames_a > 30:
        weaknesses_a.append("slow_recovery")
    if tilted_frames_b > 30:
        weaknesses_b.append("slow_recovery")

    # 3. Vulnerable Chassis
    if final_dur_a < (initial_dur_a * 0.3):
        weaknesses_a.append("vulnerable_chassis")
    if final_dur_b < (initial_dur_b * 0.3):
        weaknesses_b.append("vulnerable_chassis")

    return BattleReport(
        robot_a_name=r_a_name,
        robot_b_name=r_b_name,
        winner=winner,
        win_reason=win_reason,
        damage_dealt_a=dmg_dealt_a,
        damage_dealt_b=dmg_dealt_b,
        damage_pct_a=dmg_pct_a,
        damage_pct_b=dmg_pct_b,
        distance_covered_a=dist_a,
        distance_covered_b=dist_b,
        successful_attacks_a=attacks_a,
        successful_attacks_b=attacks_b,
        weaknesses_a=weaknesses_a,
        weaknesses_b=weaknesses_b,
    )
