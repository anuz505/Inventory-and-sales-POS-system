pipeline{
    agent any

    stages{

        stage("Checkout"){
            steps{
                git branch:"main", url: 'https://github.com/anuz505/Inventory-and-sales-POS-system.git'
            }
        }

        stage("Setup Python"){
            steps{
                bat """
                python -m venv myvenv
                myvenv\\Scripts\\python -m pip install --upgrade pip
                myvenv\\Scripts\\pip install -r requirements.txt
                """
            }
        }

        stage("Start Services"){
            steps{
                bat """
                docker compose up -d --build
                                        """
                sleep(time: 30, unit: 'SECONDS')
            }
        }
        stage("Lint Code"){
            steps{
                bat """
                    myvenv\\Scripts\\flake8
                    """
            }
        }
        stage("Format Code"){
            steps{
                bat """
                    myvenv\\Scripts\\black --check .
                    """
            }
        }
        stage("Run Tests"){
            steps{
                bat """
                myvenv\\Scripts\\pytest --cov=. ^
                --cov-report=xml ^
                --cov-report=html ^
                --junitxml=test-results.xml ^
                -v
                """
            }
        }
       

    }
}