import "./LoadForm.css"
import xlsx_img from "./xlsx.png"
export default function LoadForm() {
    function handleFileLoad(event) {
        const formData = new FormData();
        
        const file = event.target.files[0];
        // console.log(event.target.files[0]);
        formData.append(file.name, file);
        // console.log(file.name);
        fetch("/api/upload", {
            method: "POST",
            body: formData,
        }).then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }
    return(
        <form action="load" method="post" id='upload-form'>
            <label htmlFor="file-upload" className="file-upload-label">
                <div className="load-form">
                    <div className="xlsx-img">
                        <img src={xlsx_img} alt="xlsx" />
                    </div>
                    <div className="file-description">
                        <p className="fileD">Загрузить файл</p>
                        <p className="fileD">.xls .xlsx</p>
                    </div>
                </div>
            </label>
            <input id="file-upload" type="file" accept=".xls,.xlsx" onChange={handleFileLoad}/>   
        </form>
    );
}