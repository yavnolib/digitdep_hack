import "./Autolotation.css"
import LoadForm from "../LoadForm/LoadForm";
import { useState } from "react";
export default function Autolotion() {
    
    // const [AutolotationContent, setAutolotationContent] = useState(LoadForm);
    // function Load() {
    //     setAutolotationContent("Loaded");
    // }
    return(
        <div className="autolotation-content">
            <p className="h3">Автоматичкское лотирование заявок на закупку МТР</p>
            {/* { AutolotationContent } */}
            <LoadForm/>
        </div>
    );
}