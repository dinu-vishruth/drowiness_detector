# AI-Powered Alertness & Drowsiness Prevention System

A privacy-first, real-time web application designed to monitor user alertness, detect signs of drowsiness, and actively keep users awake through interactive cognitive and physical challenges. Built using a hybrid Client-Edge architecture, it runs AI computer vision models directly in the user's browser via WebAssembly (WASM), ensuring zero network lag and complete privacy.

---

## 🌟 Key Features

*   **Real-time Eye Aspect Ratio (EAR) Tracking**: Measures eyelid distance to detect microsleeps (threshold dynamically calibrated per user on startup).
*   **Mouth Aspect Ratio (MAR) Yawning Detection**: Identifies early signs of fatigue by tracking lip movement and yawning frequencies.
*   **Head Nodding & Tilt (Pose Estimation)**: Detects sudden nods (pitch drop) or side-to-side head tilt (roll).
*   **Physical Activity & Eye Rubbing Check**: Utilizes hand landmark coordinates to detect when the user is rubbing their eyes.
*   **Progressive Alarm & Alert System**: 
    *   *Level 1 Warning*: Gentle text-to-speech audio reminders.
    *   *Level 2 Critical*: Interactive full-screen alerts accompanied by a synthesized siren alarm.
*   **Active Wake-Up Challenges**: Forcibly interrupts drowsiness with cognitive tasks (Math problems, Memory sequences, Reaction clicks) and physical verification (Smile verification).
*   **Gamified Economy & Streaks**: Earn XP for focus time, maintain daily streaks, and unlock focus achievements.
*   **Interactive Dashboard**: View historical focus data, peak alertness times, and personalized break recommendations based on Pandas data analysis.
*   **Exportable Reports**: Generate professional PDF reports (via ReportLab) and CSV logs detailing all drowsiness incidents and focus timelines.

---

## 🛠️ Technology Stack

*   **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript (ES6+), Chart.js
*   **Computer Vision**: MediaPipe Face Mesh WASM, MediaPipe Hands WASM, WebRTC
*   **Backend**: Python, Flask, Flask-Login, Flask-SQLAlchemy
*   **Database**: SQLite (ORM via SQLAlchemy)
*   **Analytics Engine**: Pandas, NumPy
*   **Report Generation**: ReportLab (PDF), CSV

---

## 📐 Architecture Overview

```
                        ┌────────────────────────┐
                        │      User Webcam       │
                        └───────────┬────────────┘
                                    │ WebRTC Stream
                                    v
 ┌──────────────────────────────────────────────────────────────────────┐
 │                         Client Browser (Edge)                        │
 │                                                                      │
 │   ┌───────────────────────┐            ┌─────────────────────────┐   │
 │   │  MediaPipe Face Mesh  ├───────────>│   MediaPipe Hands WASM  │   │
 │   └──────────┬────────────┘            └────────────┬────────────┘   │
 │              │ 478 landmarks                        │ 21 landmarks   │
 │              └───────────────────┬──────────────────┘                │
 │                                  v                                   │
 │                     ┌──────────────────────────┐                     │
 │                     │ Alertness Engine (EAR)   │                     │
 │                     └────────────┬─────────────┘                     │
 │                                  │                                   │
 │       ┌──────────────────────────┼──────────────────────────┐        │
 │       │ Alert Thresholds Passed  │ Normal Monitoring State  │        │
 │       v                          v                          v        │
 │  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐│
 │  │ Audio Siren  │          │   TTS Speech │          │ HUD Updates  ││
 │  └──────────────┘          └──────────────┘          └──────────────┘│
 └──────────────────────────────────┬───────────────────────────────────┘
                                    │ JSON Payload (HTTPS POST)
                                    v
 ┌──────────────────────────────────────────────────────────────────────┐
 │                           Flask Backend                              │
 │                                                                      │
 │   ┌───────────────────────┐            ┌─────────────────────────┐   │
 │   │    Route Controllers  ├───────────>│   Pandas Analytics      │   │
 │   └──────────┬────────────┘            └────────────┬────────────┘   │
 │              v                                      v                │
 │   ┌───────────────────────┐            ┌─────────────────────────┐   │
 │   │   SQLAlchemy Models   │            │   ReportLab PDF Engine  │   │
 │   └──────────┬────────────┘            └─────────────────────────┘   │
 │              v                                                       │
 │      SQLite Database                                                 │
 └──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.8 or higher
*   A modern web browser with webcam access

### Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/dinu-vishruth/drowiness_detector.git
    cd drowiness_detector
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    *   **Windows**:
        ```powershell
        venv\Scripts\activate
        ```
    *   **macOS / Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies**:
    ```bash
    pip install Flask Flask-Login Flask-SQLAlchemy pandas numpy reportlab
    ```

5.  **Run the Application**:
    ```bash
    python app.py
    ```

6.  **Access the Application**:
    *   Open your browser and navigate to `http://127.0.0.1:5000`
    *   Sign up for a new account, or log in using the default developer credentials:
        *   **Username**: `developer`
        *   **Password**: `developer123`

---

## 📋 How It Works (The Core Math)

*   **Eye Aspect Ratio (EAR)**: Computes the ratio of eye openness. When the average value drops below the user's calibrated threshold for 6 consecutive frames (~0.5s), it triggers a drowsiness state.
*   **Mouth Aspect Ratio (MAR)**: Computes mouth elongation to detect yawns. A value exceeding `0.55` triggers a yawn event.
*   **Head Nodding & Tilt**: Roll is computed using `Math.atan2` between outer eye corners. Pitch is computed via the nose-to-chin ratio compared to the mid-eyes baseline.
*   **Eye Rubbing**: Measures the Euclidean distance between fingertips and eye corners; values below `0.08` trigger an eye-rubbing warning.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
