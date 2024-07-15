all: clean zip

zip:
	cd part-C && pdflatex partC.tex
	cp part-D/pox/pox/cs456/a3.py part-D/a3.py
	mkdir j76xiao
	cp -r part-A/ part-B/ part-D/ j76xiao/
	rm -rf j76xiao/part-D/pox/
	mkdir j76xiao/part-C
	cp -r part-C/screenshot part-C/partC.pdf j76xiao/part-C/
	zip -r CS456-A3-j76xiao.zip j76xiao/

clean:
	rm -rf CS456-A3-j76xiao.zip j76xiao/ part-C/partC.pdf part-D/a3.py
