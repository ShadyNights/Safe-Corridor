import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapUpdater({ center }) {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.flyTo(center, map.getZoom(), { duration: 1 });
        }
    }, [center, map]);
    return null;
}

const MapView = ({ path, currentPos, startPos, endPos }) => {
    const center = currentPos ? [currentPos.lat, currentPos.lon] : (startPos ? [startPos.lat, startPos.lon] : [21.1458, 79.0882]);
    const sPos = startPos ? [startPos.lat, startPos.lon] : null;
    const ePos = endPos ? [endPos.lat, endPos.lon] : null;
    const cPos = currentPos ? [currentPos.lat, currentPos.lon] : null;
    const formattedPath = path ? path.map(p => [p.lat, p.lon]) : [];

    return (
        <div className="h-full w-full rounded-lg overflow-hidden border border-slate-700">
            <MapContainer center={center} zoom={14} scrollWheelZoom={true} preferCanvas={true} className="h-full w-full">
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapUpdater center={cPos || center} />

                {sPos && <Marker position={sPos}><Popup>Start</Popup></Marker>}
                {ePos && <Marker position={ePos}><Popup>End</Popup></Marker>}

                {formattedPath.length > 0 && (
                    <Polyline positions={formattedPath} color="blue" />
                )}

                {cPos && (
                    <CircleMarker center={cPos} radius={8} color="red" fillOpacity={0.8}>
                        <Popup>Current Location</Popup>
                    </CircleMarker>
                )}
            </MapContainer>
        </div>
    );
};

export default MapView;
