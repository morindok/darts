# Django Project: Darts

This project is developed to support artists financially. Artists can upload their artworks, gift them to others, or put them up for auction to sell.

I would be delighted if you could help contribute to the development of the project.

To run the project, follow these steps:

## How to Run the Project

### Prerequisites
1. **Install Python and PyCharm:**
   - [Download Python](https://www.python.org/downloads/)
   - [Download PyCharm](https://www.jetbrains.com/pycharm/download/)

2. **Clone the project from GitHub:**
   ```bash
   git clone https://github.com/morindok/darts.git
   
3. **install virtual environment on terminal:**
	```bash
	cd darts
	python -m venv venv
	source venv/bin/activate

4. **install django:**
	```bash
	pip install django
	pip install pillow

5. **make migrations:**
	```bash
	python manage.py makemigrations
	python manage.py migrate

6. **run project on local:**
	```bash
	ptyhon manage.py runserver