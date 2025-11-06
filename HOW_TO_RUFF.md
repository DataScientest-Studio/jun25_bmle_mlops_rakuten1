# Pour paramétrer correctement Ruff dans VS Code pour un projet

## Étapes principales

### Installer l’extension Ruff pour VS Code

> Rechercher Ruff dans la marketplace (éditeur VS Code), puis l’installer .

​![Image of the Ruff extension in vs_code.](/ressources/images/VSC_EXTENSION_RUFF_ASTRAL_SOFTWARE.png "Ruff extension in vs_code.")

### Configurer le formatage et linting dans settings.json

> Ajoute ce bloc dans ton .vscode/settings.json ou via la palette de commandes :
```
json
{
"[python]": {
"editor.formatOnSave": true,
"editor.defaultFormatter": "charliermarsh.ruff"
}
}
```
> Cela active Ruff en tant que formatter et linter sur sauvegarde .

​

### Configurer Ruff via le projet

> Déclare les règles Ruff, les options lint et format dans pyproject.toml ou ruff.toml à la racine du projet :
```
text
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]  # erreurs, fautes, imports
ignore = ["E501"]  # ignorer la longueur de ligne, par exemple
```

> Ruff lira automatiquement cette configuration locale et l’appliquera dans VS Code .

​### Options avancées

> Tu peux passer des arguments supplémentaires via VS Code, exemple dans settings.json :
```
json
"ruff.lint.args": ["--extend-select=UP"]
```

> pour le mode Pyupgrade, etc. .
​
### Conseils

> Désinstalle les autres outils de linting comme flake8 ou pylint pour éviter les conflits.
> Assure-toi que le workspace VS Code soit bien à la racine du projet contenant le pyproject.toml, pour que l’extension Ruff détecte la configuration.

> Avec cette configuration, Ruff gérera automatiquement le linting et le formatage de ton code Python dans VS Code, en respectant ta configuration projet.
​

## Configurer Ruff comme linter unique et désactiver les autres

> Pour utiliser Ruff comme linter unique dans VS Code et désactiver tous les autres linters :
 
###  1. Désactiver les autres linters dans VS Code

> Ajoute ceci dans ton fichier .vscode/settings.json :
```
json
{
"python.linting.enabled": true,
"python.linting.ruffEnabled": true,
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": false,
"python.linting.pycodestyleEnabled": false,
"python.linting.banditEnabled": false,
"python.linting.mypyEnabled": false
}
```
> Cela force la désactivation de pylint, flake8, pycodestyle, bandit, mypy.​

### 2. Activer Ruff comme linter unique

> Toujours dans .vscode/settings.json :
```
json
{
"python.linting.ruffEnabled": true,
"python.linting.enabled": true
}
```

### 3. Formatter Ruff (optionnel)

> Pour que Ruff soit aussi ton formatter Python :
```
json
{
"[python]": {
"editor.defaultFormatter": "charliermarsh.ruff",
"editor.formatOnSave": true
}
}
```

### 4. Vérifie les extensions installées

> Supprime éventuellement l’extension Flake8 ou Pylint de VS Code pour ne garder que l’extension officielle Ruff.


Avec cette configuration, Ruff sera le seul linter utilisé dans VS Code et les autres seront désactivés. 
Cela garantit des analyses cohérentes et plus rapides sur ton code Python.
​