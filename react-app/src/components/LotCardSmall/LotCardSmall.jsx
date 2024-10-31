import "./LotCardSmall.css"
import LotCardBig from "../LotCardBig/LotCardBig";
import { useRef } from "react";


export default function LotCardSmall({lotNum, description, startDate, endDate, status=true, setBigCard, mainContentRef}){
    function handleCardClick() {
        console.log("HUI");
        setBigCard(<LotCardBig lotNum={lotNum} description={description} startDate={startDate} endDate={endDate} status={status} setBigCard={setBigCard} mainContentRef={mainContentRef}/>);
        // document.body.classList.add('no-scroll');
        document.body.style.overflow = 'hidden';
        mainContentRef.current.style.overflow = 'hidden';
        // console.log(document.querySelector('.for-blur')
    }
    return(
        <div className="small-card" role="button" onClick={handleCardClick}>
            <div className="card-header">
                <div className="lot-num">
                    Лот №{lotNum}
                </div>
                <div className="lot-status">
                    {status ? "active" : "disactive"}
                </div>
            </div>
            <div className="description">
                {description}
            </div>
            <div className="dates">
                <div className="start-date date">
                    Дата начала приема заявок: {startDate}
                </div>
                <div className="end-date date">
                    Дата конца приема заявок: {endDate}
                </div>
            </div>
        </div>
    );
}