pipeline{
    agent any

            steps{
                echo("Running pytest")
                bat """
                    call myvenv\Scripts\activate
                    cd Inventory-and-sales-POS-system
                    set DJANGO_SETTINGS_MODULE=internship_task.test_settings
                    pytest --cov=. --cov-report=xml:coverage.xml ^
                    --cov-report=html:htmlcov ^
                    --junitxml=test-results.xml -v ^
                    --tb=short
                    """
            steps{
                bat """
                python -m venv myvenv
                call myvenv\\Scripts\\activate
                pip install --upgrade pip 
                pip install -r Inventory-and-sales-POS-system/requirements.txt
                """
            }
        }
        stage("Unit test"){
            steps{
                echo("Running pytest")
                bat """
                    call myvenv\\Scripts\\activate
                    cd Inventory-and-sales-POS-system
                    pytest --cov=. --cov-report=xml:coverage.xml ^
                    --cov-report=html:htmlcov ^
                    --junitxml=test-results.xml -v ^
                    --tb=short
                    """
            }
        }
    
    }
}