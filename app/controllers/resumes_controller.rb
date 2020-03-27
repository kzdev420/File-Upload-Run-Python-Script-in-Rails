class ResumesController < ApplicationController
  def index
    @resumes = Resume.all
  end
  
  def new
      @resume = Resume.new
      # source python_script/venv/bin/activate
      pyscript_path = Rails.root.join('main.py')
      tag_var = `python #{pyscript_path} python_script/Hema_Jumani.docx`.chomp
      tag_var = JSON.parse(tag_var)
      tag_var.each do |key, value|
        puts key
        puts value        
      end
  end
  
  def create
      @resume = Resume.new(resume_params)
      
      if @resume.save
        redirect_to resumes_path, notice: "The resume #{@resume.name} has been uploaded."
      else
        render "new"
      end
      
  end
  
  def destroy
      @resume = Resume.find(params[:id])
      @resume.destroy
      redirect_to resumes_path, notice:  "The resume #{@resume.name} has been deleted."
  end
  
  private
      def resume_params
      params.require(:resume).permit(:name, :attachment)
  end

end
