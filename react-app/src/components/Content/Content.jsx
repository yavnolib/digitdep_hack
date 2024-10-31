import "./Content.css"
export default function Content( {mainContent, bigCard, mainContentRef} )
{
    return(
        <div className="main-content" ref={mainContentRef}>
            {mainContent}
            {bigCard}
        </div>
    );
}