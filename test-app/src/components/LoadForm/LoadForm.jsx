import "./LoadForm.css"
import xlsx_img from "./xlsx.png"

export default function LoadForm() {
    return(
        <div className="load-form">
            <form action="load" method="post">
                <div className="xlsx-img">
                    <img src={xlsx_img} alt="xlsx" />
                </div>
                <div className="file-description">
                    <p className="fileD">Загрузить файл</p>
                    <p className="fileD">.xls .xlsx</p>
                </div>
            </form>
        </div>
    );
}