# 🗓️ Appointment Scheduling System in Python

This is an appointment scheduling system with a graphical interface developed in **Python (Tkinter)**.  
It allows you to register, view, edit, delete, and complete appointments, storing data in **CSV files** for easy access.

---

## ✨ Features

✅ Appointment registration with:
- Name
- Email
- Service (3D Printing, Laser Cutting, General Assistance)
- Date and Time (with automatic formatting)
- Service-specific extra information

✅ Automatic validation:
- Valid email  
- Future date/time  
- Required fields  

✅ Management:
- View all appointments in an interactive table  
- Filter by name, service, or date  
- Edit existing appointments  
- Delete appointments  
- Mark appointments as **completed** (moving them to another CSV file)

✅ History:
- View completed appointments in a separate window  
- Separate record in **`servicos_concluidos.csv`**

---

## 🛠️ Technologies used

- **Python 3**  
- **Tkinter** → Graphical interface  
- **CSV** → Data storage  
- **Regex** → Email validation  
- **Datetime** → Date and time validation  

---

## 📂 File structure

- `Agendamentos.py` → Main system code  
- `agendamentos.csv` → Database of active appointments  
- `servicos_concluidos.csv` → Database of completed appointments  

---

## ▶️ How to run

1. Clone the repository or copy the files to a local folder.  
2. Make sure **Python 3** is installed.  
3. Run the system:  



Project developed by Kauan Zembruski
```bash
python Agendamentos.py




