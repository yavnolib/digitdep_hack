import "./Sidebar.css"
import Instructions from "../Instructions/Instructions";
import Autolotion from "../Autolotation/Autolotation";
import { useState, useEffect } from "react";

export default function Sidebar() {
    const [content, setContent] = useState(Autolotion);
    const [isAutolotationButtonPressed, setIsAutolotationButtonPressed] = useState(false);
    const [isInstructionsButtonPressed, setIsInstructionsButtonPressed] = useState(false);
    function clickHandleInstructions() {
        setContent(Instructions);
        setIsInstructionsButtonPressed(true);
        setIsAutolotationButtonPressed(false);
    }
    useEffect(() => {
        if (!isAutolotationButtonPressed && !isInstructionsButtonPressed){
            setIsAutolotationButtonPressed(true);
        }
        
    });

    function clickHandleAutolotation() {
        setContent(Autolotion);
        setIsAutolotationButtonPressed(true);
        setIsInstructionsButtonPressed(false);
    }
    
    return (
        <div className="sidebar">


            <div className="btns">
                <button id="instructionbtn" onClick={clickHandleInstructions} disabled={isInstructionsButtonPressed}>Инструкции</button>
                <button id="autolotbtn" onClick={clickHandleAutolotation} disabled={isAutolotationButtonPressed}>Автолотирование</button>
            </div>
            <div className="sidebar-content">
                {content}
            </div>
        </div>
    )
}