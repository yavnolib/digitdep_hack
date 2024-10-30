import "./LotCardBig.css"

export default function LotCardBig({lotNum, description, startDate, endDate, status, setBigCard, mainContentRef}) {
    function handleCloseClick(){
        setBigCard("")
        document.body.style.overflow = '';
        mainContentRef.current.style.overflow = '';
    }
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
                    {description}
                </div>
            </div>
        </div>
    );
}