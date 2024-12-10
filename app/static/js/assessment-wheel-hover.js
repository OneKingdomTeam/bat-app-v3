
class AssessmentHover {

    constructor(){
        this.wheel = document.querySelector(".bat-interactive-circle")
        this.categories = this.wheel.querySelectorAll(".category")
    }


    hookHoverInfo(){
        this.categories.forEach(element => {
            element.addEventListener("mouseover", (e)=>{
                console.log(e.target.dataset.category_name)
            })
            element.addEventListener("mouseout", (e)=>{

            })
        });
    }

}
