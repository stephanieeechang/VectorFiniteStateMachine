# Run git add, commit, and push in one terminal command:
# make git m="commit message"
git:
	git add .
	git commit -m "$m"
	git push -u origin master

