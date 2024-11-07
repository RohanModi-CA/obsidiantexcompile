import re
from random import choice
from os import system,sys,path,makedirs

def get_file(file_name):
    file = open(file_name, "r")
    file_contents = file.read()
    file.close()
    return file_contents

def remove_dollar_signs(file_contents):
    file_contents_list = file_contents.split("\n")
    modified_file_contents_list = []
    inside_dollar_signs = False

    is_start_or_end_of_block = lambda num: ("$$" in line and "\\begin{" in file_contents_list[num+1]) or ("$$" in line and "\\end{" in file_contents_list[num-1])

    for num,line in enumerate(file_contents_list):
        line = line.replace(r"\newpage", "")
        """ also kill the div tags    """
        line = re.sub(r'<div.*?>.*?</div>', '', line, flags=re.DOTALL)

        if is_start_or_end_of_block(num):
            inside_dollar_signs = not inside_dollar_signs
            modified_file_contents_list.append(line.replace("$$", ""))
        else:
            modified_file_contents_list.append(line)
    
    modified_file_contents = "\n".join(modified_file_contents_list)
    return modified_file_contents

def style_callouts(file_contents):
    file_contents_list = file_contents.split("\n")
    modified_file_contents_list = []

    callout_to_color = {
        "[!note]": "cyan",
        "[!info]": "cyan",
        "[!todo]": "cyan",
        "[!abstract]": "teal",
        "[!summary]": "teal",
        "[!tldr]": "teal",
        "[!tip]": "magenta",
        "[!hint]": "magenta",
        "[!important]": "magenta",
        "[!success]": "green",
        "[!check]": "green",
        "[!done]": "green",
        "[!question]": "orange",
        "[!help]": "orange",
        "[!faq]": "orange",
        "[!warning]": "orange",
        "[!caution]": "orange",
        "[!attention]": "orange",
        "[!failure]": "red",
        "[!fail]": "red",
        "[!missing]": "red",
        "[!danger]": "red",
        "[!error]": "red",
        "[!bug]": "red",
        "[!example]": "purple",
        "[!quote]": "lightgray",
        "[!cite]": "lightgray"
    }
    is_inside = False

    for num,line in enumerate(file_contents_list):
        if line.startswith(">"):
            is_inside = True if file_contents_list[num+1].startswith(">") or file_contents_list[num-1].startswith(">") else False
            is_at_end = False if file_contents_list[num+1].startswith(">") else True
            is_at_start = False if file_contents_list[num-1].startswith(">") else True
            newline = '\\\\' if '\\\\' not in line and '\\begin' not in line and '\\end' not in line else ''
            
            if not is_at_end and not is_at_start: # multiline quote case
                modified_file_contents_list.append(line[1:] + newline)
            elif is_at_end:
                modified_file_contents_list.append("\\end{tcolorbox}")
            elif is_inside:
                for key in callout_to_color.keys():
                    if key in line:
                        title = line[len(key)+2:]
                        if title == "":
                            title = key[2:-1].capitalize() # Default title to example, info, etc.
                        color = callout_to_color[key]
                        modified_file_contents_list.append("\\begin{tcolorbox}"+f"[colframe={color}!25,colback={color}!10,coltitle={color}!20!black,title={{{title}}}]")
                        break
            else:
                modified_file_contents_list.append(f'{line}{newline}') # single line quote case
        else:
            modified_file_contents_list.append(line)
    
    modified_file_contents = "\n".join(modified_file_contents_list)
    return modified_file_contents


def embed_images(file_contents):
    file_contents_list = file_contents.split("\n")
    modified_file_contents_list = []
    for line in file_contents_list:
        if '![[' in line and ('.png' in line or '.jpg' in line):
            image_name = line[line.find('[[')+2:line.find(']]')]
            if '|' in image_name:
                width = image_name.split('|')[1]
                image_name = image_name.split('|')[0]
            else:
                width = 500

            img_path = "/Users/oliviachoi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Olivia" # Location you store your images
            modified_file_contents_list.append(f'\\includegraphics[width={width}px]{{{img_path}/{image_name}}}')            
        else:
            modified_file_contents_list.append(line)

    modified_file_contents = "\n".join(modified_file_contents_list)
    return modified_file_contents

def write_file(modified_file_contents):
    name = ''.join(choice('0123456789ABCDEF') for i in range(16))
    file = open(f"/tmp/{name}.md", "w")
    file.write(modified_file_contents)
    file.close()
    return f"/tmp/{name}.md"

def convert_to_pdf(file_name, modified_file, modified_file_contents, root_path):
    folder = "/".join(file_name.split("/")[:-1])
    md = file_name.split("/")[-1][:-3]
    if "\\ " in md:
        md = md.replace("\\ ", " ")

    if not path.exists(f"{folder}/output"):
        makedirs(f"{folder}/output")

    resources = "/Users/oliviachoi/Documents/preamble.tex" # Location of your preamble.tex file

    with open(f"{root_path}docsetup.txt", "r") as docfile:
        docsetup = docfile.read()
    
    tex_file = docsetup + modified_file_contents + " \n \n \\end{document}\n"

    with open(f"{root_path}pdftex/{md}.tex", "a") as doctocompiletex:
        doctocompiletex.write(" ")
    with open(f"{root_path}pdftex/{md}.tex", "w") as doctocompiletex:
        doctocompiletex.write(tex_file)

    # command_to_run =f"/usr/local/bin/pandoc --pdf-engine=/Library/TeX/texbin/pdflatex  -o \"{folder}/output/{md}.pdf\" {modified_file} -V geometry:margin=0.5in -H {resources} --variable documentclass=article"

    command2=f"/Library/TeX/texbin/xelatex -output-directory={root_path}pdftex/  -interaction=nonstopmode '{root_path}pdftex/{md}.tex'"

    # system(command_to_run)
    system(command2)
    system(f"rm {modified_file}") # cleanup the temporary file
    
    return f"'{root_path}pdftex/{md}.pdf'"
    """ this is the old return   """
    # return f"\"{folder}/output/{md}.pdf\"" 

def main():
    file_name = sys.argv[1]
    file_contents = get_file(file_name)


    root_path = "/Users/oliviachoi/Documents/obsidiantex/"

    modified_file_contents = remove_dollar_signs(file_contents)
    modified_file_contents = style_callouts(modified_file_contents)
    modified_file_contents = embed_images(modified_file_contents)

    modified_file = write_file(modified_file_contents)
    m1file = convert_to_pdf(file_name,modified_file, modified_file_contents,root_path)
    file_name = file_name.split("/")[-1]
    print(f"Converted {file_name} to PDF.")
    system(f"open {m1file}")

if __name__ == "__main__":
    main()
