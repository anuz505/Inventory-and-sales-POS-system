pipeline{
    agent any
        stages{
            stage("Git clone "){
                steps{
                    bat "git clone https://github.com/anuz505/Inventory-and-sales-POS-system.git"
                }
            }
            stage("Depenedencies installation"){

            steps{
                bat """
                python -m venv myvenv
                call myvenv\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r Inventory-and-sales-POS-system/requirements.txt
                """
            }       
            }
        
        stage("Unit test"){
            steps{
            echo("Docker compose ")
            bat """
            cd Inventory-and-sales-POS-system
            docker compose up -d --build 

            """
            echo("Running pytest")
                bat """
                    call myvenv\\Scripts\\activate
                    set DJANGO_SETTINGS_MODULE=internship_task.test_settings
                    python manage.py migrate
                    pytest --cov=. --cov-report=xml:coverage.xml ^
                    --cov-report=html:htmlcov ^
                    --junitxml=test-results.xml -v ^
                    --tb=short
                    """
            }
        }
    
    }
}        
