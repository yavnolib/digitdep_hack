import "./Sidebar.css"
import Instructions from "../Instructions/Instructions";
import Autolotion from "../Autolotation/Autolotation";
import { useState, useEffect } from "react";

export default function Sidebar({setMainContent, setBigCard, mainContentRef, dataLoaded, setDataLoaded, setLotCount}) {
    // console.log(setMainContent)
    // setDataLoaded("LI")
    const [sidebarContent, setContent] = useState(<Autolotion setMainContent={setMainContent} setBigCard={setBigCard} mainContentRef={mainContentRef} dataLoaded={dataLoaded} setDataLoaded = {setDataLoaded} setLotCount={setLotCount} />);
    const [isAutolotationButtonPressed, setIsAutolotationButtonPressed] = useState(false);
    const [isInstructionsButtonPressed, setIsInstructionsButtonPressed] = useState(false);
    function clickHandleInstructions() {
        // setDataLoaded("LI")
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
        setContent(<Autolotion setMainContent={setMainContent} setBigCard={setBigCard} mainContentRef={mainContentRef} dataLoaded={dataLoaded} setDataLoaded={setDataLoaded} setLotCount={setLotCount} />);
        setIsAutolotationButtonPressed(true);
        setIsInstructionsButtonPressed(false);
    }
    
    return (
        <div className="sidebar">


            <div className="btns">
                <button className="sidebar-btn" id="instructionbtn" onClick={clickHandleInstructions} disabled={isInstructionsButtonPressed}>Инструкции</button>
                <button className="sidebar-btn" id="autolotbtn" onClick={clickHandleAutolotation} disabled={isAutolotationButtonPressed}>Автолотирование</button>
            </div>
            <div className="sidebar-content">
                {sidebarContent}
            </div>
        </div>
    )
}