.PHONY: doctor list play leaderboard help

APP_DIR := git-learning-game
PLAYER ?= $(USER)
STAGE ?= 1
LIMIT ?= 10

doctor:
	cd $(APP_DIR) && ./git-trainer.sh doctor

list:
	cd $(APP_DIR) && ./git-trainer.sh list

play:
	cd $(APP_DIR) && ./git-trainer.sh play --player "$(PLAYER)" --stage "$(STAGE)"

leaderboard:
	cd $(APP_DIR) && ./git-trainer.sh leaderboard --limit "$(LIMIT)"

help:
	@echo "Available targets:"
	@echo "  make doctor"
	@echo "  make list"
	@echo "  make play PLAYER=<name> STAGE=<number>"
	@echo "  make leaderboard LIMIT=<number>"
	@echo "  make help"

