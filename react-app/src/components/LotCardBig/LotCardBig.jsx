import "./LotCardBig.css"
import { useEffect } from "react";

export default function LotCardBig({lotNum, uniqueMats, uniqueBuyers, numMembers, description, lotSum, isTop, setBigCard, mainContentRef}) {
    function handleCloseClick(){
        setBigCard("")
        document.body.style.overflow = '';
        mainContentRef.current.style.overflow = '';
    }
    useEffect(() => {
        const handleEsc = (event) => {
            if (event.key === 'Escape') {
                setBigCard("")
                document.body.style.overflow = '';
                mainContentRef.current.style.overflow = '';
            }
        };
        window.addEventListener('keydown', handleEsc);
    
        return () => {
          window.removeEventListener('keydown', handleEsc);
        };
      }, []);
    
    let descriptionBig = [];
    return(
        <div className="for-blur">
            <div className="big-card">
                <div className="lot-header">
                    <div className="lot-num-big">
                        Лот №{lotNum}
                    </div>
                    <div className="space">
                        maxos
                    </div>
                    <div className="closeModal" role="button" onClick={handleCloseClick}></div>
                </div>
                <div className="description-big">
                    {Object.keys(description).forEach(i => {
                        descriptionBig.push(<li className="description-big-item">{i}: {description[i]}</li>)
                    })}
                    <ul className="description-description-big-list">
                        {descriptionBig}
                    </ul>
                </div>
            </div>
        </div>
    );
}