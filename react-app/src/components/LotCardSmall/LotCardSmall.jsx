import "./LotCardSmall.css"
import LotCardBig from "../LotCardBig/LotCardBig";
import { useRef, useState } from "react";
import fire from "./fire.png"


export default function LotCardSmall({lotNum, uniqueMats, uniqueBuyers, numMembers, description, lotSum, isTop, setBigCard, mainContentRef}){
    function handleCardClick() {
        // console.log("HUI");
        setBigCard(<LotCardBig lotNum={lotNum} uniqueMats={uniqueMats} uniqueBuyers={uniqueBuyers} numMembers={numMembers} description={description} lotSum={lotSum} isTop={isTop}  setBigCard={setBigCard} mainContentRef={mainContentRef}/>);
        // document.body.classList.add('no-scroll');
        document.body.style.overflow = 'hidden';
        mainContentRef.current.style.overflow = 'hidden';
        // console.log(document.querySelector('.for-blur')
    }
    let descriptionSmall = [];
    return(
        <div className="small-card" role="button" onClick={handleCardClick}>
            <div className="card-header">
                <div className="lot-num">
                    <div className="lot-num-num">
                        Лот №{lotNum}
                    </div>
                    <div className="lot-status">
                        {isTop ? <img src={fire} alt="fire" className="fire" /> : ""}
                    </div>
                </div>
                <div className="small-space"></div>
            </div>
            <div className="description">
                {/* {description}     */}
                {Object.keys(description).forEach(i => {
                    descriptionSmall.push(<li className="description-small">{i}: {description[i]}</li>)
                })}
                <ul className="description-small">
                    {descriptionSmall}
                </ul>
                {/* {console.log(description)} */}
                {/* {numMembers} */}
            </div>
            <div className="dates">
                <div className="start-date date">
                    Количество материалов: {uniqueMats}
                </div>
                <div className="end-date date">
                    Стоимость лота: {lotSum}
                </div>
            </div>
        </div>
    );
}