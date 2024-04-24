import React from 'react';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import Tooltip from "@mui/material/Tooltip";
import { Link } from 'react-router-dom'
import HomeIcon from '@mui/icons-material/Home';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import SignalWifi1BarIcon from '@mui/icons-material/SignalWifi1Bar';
import SignalWifi1BarLockIcon from '@mui/icons-material/SignalWifi1BarLock';
import SignalWifi2BarIcon from '@mui/icons-material/SignalWifi2Bar';
import SignalWifi2BarLockIcon from '@mui/icons-material/SignalWifi2BarLock';
import SignalWifi3BarIcon from '@mui/icons-material/SignalWifi3Bar';
import SignalWifi3BarLockIcon from '@mui/icons-material/SignalWifi3BarLock';
import SignalWifi4BarIcon from '@mui/icons-material/SignalWifi4Bar';
import SignalWifi4BarLockIcon from '@mui/icons-material/SignalWifi4BarLock';
import WifiTetheringIcon from '@mui/icons-material/WifiTethering';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';


class Network extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show_connect_dialog: false,
            show_forget_dialog: false,
            selected_network: null,
            password: "",
            robot_config: {},
            wifi_status: {"state": "connected", "connection": "FiOS-6OCTG-5G", "hotspot": false, "signal": 69},
            wifi_networks: [{"in_use": false, "ssid": "FiOS-6OCTG", "bssid": "A0:04:60:89:FA:5F", "mode": "Infra", "chan": 8, "freq": 2447, "rate": 195, "signal": 100, "security": "WPA2", "saved": true}, {"in_use": false, "ssid": "", "bssid": "32:86:8C:23:9C:06", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 195, "signal": 69, "security": "WPA1 WPA2", "saved": false}, {"in_use": false, "ssid": "", "bssid": "52:86:8C:23:9C:06", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 195, "signal": 69, "security": "WPA1 WPA2 802.1X", "saved": false}, {"in_use": true, "ssid": "FiOS-6OCTG-5G", "bssid": "A0:04:60:89:FA:5E", "mode": "Infra", "chan": 36, "freq": 5180, "rate": 405, "signal": 69, "security": "WPA2", "saved": true}, {"in_use": false, "ssid": "Sweden", "bssid": "10:86:8C:23:9C:06", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 195, "signal": 67, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "Sweden", "bssid": "10:86:8C:23:9C:0C", "mode": "Infra", "chan": 157, "freq": 5785, "rate": 405, "signal": 64, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "DIRECT-EA-HP OfficeJet Pro 6960", "bssid": "84:A9:3E:F3:B0:EB", "mode": "Infra", "chan": 8, "freq": 2447, "rate": 65, "signal": 57, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "FoleyFun", "bssid": "DE:FA:25:0E:3B:F6", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 32, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "", "bssid": "CE:FA:25:0E:3B:F6", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 32, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "wifi-X", "bssid": "D4:B9:2F:13:08:2F", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 30, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "", "bssid": "D4:B9:2F:13:08:34", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 30, "security": "WPA1 WPA2 802.1X", "saved": false}, {"in_use": false, "ssid": "D'OH", "bssid": "60:DB:98:6D:E8:A5", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 30, "security": "WPA1 WPA2", "saved": false}, {"in_use": false, "ssid": "", "bssid": "D4:B9:2F:13:08:32", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 30, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "RCM", "bssid": "08:02:8E:A2:B6:99", "mode": "Infra", "chan": 2, "freq": 2417, "rate": 260, "signal": 24, "security": "WPA2", "saved": false}, {"in_use": false, "ssid": "XP2PB", "bssid": "10:78:5B:5D:6A:E9", "mode": "Infra", "chan": 1, "freq": 2412, "rate": 130, "signal": 14, "security": "WPA2", "saved": false}],
        }
    }

    componentDidMount() {
        this.pollWifiNetworks()
    }

    pollWifiNetworks = () => {
        this.getWifiNetworks()
        setTimeout(this.pollWifiNetworks, 5000)
    }

    getWifiNetworks = () => {
        let url_prefix = window.location.port === "3000" ? "http://localhost:8080" : ""
        let url = url_prefix + '/api/v1/wifi'
        fetch(url)
            .then(response => response.json())
            .then(data => {
                this.setState({wifi_networks: data.networks, wifi_status: data.status})
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    getWifiIcon = (network) => {
        let has_security = network.security !== ""
        if (network.signal < 25) {
            return  has_security ? (<SignalWifi1BarLockIcon/>) : (<SignalWifi1BarIcon/>)
        } else if (network.signal < 50) {
            return  has_security ? (<SignalWifi2BarLockIcon/>) : (<SignalWifi2BarIcon/>)
        } else if (network.signal < 75) {
            return  has_security ? (<SignalWifi3BarLockIcon/>) : (<SignalWifi3BarIcon/>)
        } else {
            return  has_security ? (<SignalWifi4BarLockIcon/>) : (<SignalWifi4BarIcon/>)
        }
    }

    handleConnectToNetwork = (network) => {
        this.setState({show_connect_dialog: true, selected_network: network})
    }

    handleForgetNetwork = (network) => {
        this.setState({show_forget_dialog: true, selected_network: network})
    }

    connectToNetwork = () => {
        let password = this.state.selected_network.saved || this.state.selected_network.password === "" ? null : this.state.password;
        this.postWifi({ssid: this.state.selected_network.ssid, password: password})
    }

    startHotspot = () => {
        this.postWifi({hotspot: true})
    }

    startWifi = () => {
        this.postWifi({ssid: null})
    }

    postWifi = (body) => {
        let url_prefix = window.location.port === "3000" ? "http://localhost:8080" : "";
        let url = url_prefix + '/api/v1/wifi';
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        };
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        this.getWifiNetworks()
        this.setState({show_connect_dialog: false, password: ""})
    }

    forgetNetwork = () => {
        let url_prefix = window.location.port === "3000" ? "http://localhost:8080" : "";
        let url = url_prefix + '/api/v1/wifi';
        const options = {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ssid: this.state.selected_network.ssid})
        };
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        this.getWifiNetworks()
        this.setState({show_forget_dialog: false})
    }

    getConnectionIcon = (network) => {
        if (network.in_use) {
            return (<CheckCircleIcon/>)
        } else {
            return (<Tooltip title="Connect"><IconButton onClick={this.handleConnectToNetwork.bind(this, network)}><CheckCircleOutlineIcon/></IconButton></Tooltip>)
        }
    }

    handleCloseDialog = () => {
        this.setState({show_connect_dialog: false, show_forget_dialog: false, password: ""})
    }

    onChangePassword = (event) => {
        this.setState({password: event.target.value})
    }

    useHotspot = () => {
        return "hotspot" in this.state.wifi_status && this.state.wifi_status.hotspot;
    }

    getConnectionName = () => {
        return "connection" in this.state.wifi_status && this.state.wifi_status.connection;
    }

    render() {
        document.body.style.overflow = "";
        return (
        <div className="App ">
            <Box sx={{display: 'flex', width: 'fit-content', bgcolor: 'grey', margin: 1, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1}}>
                <Tooltip title="Home"><IconButton component={Link} to="/" ><HomeIcon/></IconButton></Tooltip>
            </Box>
            <p>Wifi configuration</p>
            <p>Connected to '{this.getConnectionName()}' {this.useHotspot() && "(Hotspot)"}</p>
            <Box sx={{display: 'flex', width: 'fit-content', bgcolor: 'grey', margin: 1, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1}}>
                {!this.useHotspot() && (<Tooltip title="Connect to hotspot"><IconButton onClick={this.startHotspot}><WifiTetheringIcon/></IconButton></Tooltip>)}
                {this.useHotspot() && (<Tooltip title="Disconnect hotspot"><IconButton onClick={this.startWifi}><SignalWifi4BarIcon/></IconButton></Tooltip>)}
            </Box>
            {!this.useHotspot() && (<TableContainer sx={{display: 'flex', width: 'fit-content', bgcolor: 'grey', margin: 1, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1}}>
              <Table size='small' aria-label="simple table">
                {this.state.wifi_networks.map((network) => network.ssid !== "" && (
                <TableBody>
                  <TableRow>
                    <TableCell sx={{'font-size': '20px' }}>{this.getWifiIcon(network)}</TableCell>
                    <TableCell sx={{'font-size': '20px' }}>{network.ssid}</TableCell>
                    <TableCell sx={{'font-size': '20px' }} align="center">{network.saved && (<Tooltip title="Forget"><IconButton onClick={this.handleForgetNetwork.bind(this, network)}><DeleteIcon/></IconButton></Tooltip>)}</TableCell>
                    <TableCell sx={{'font-size': '20px' }} align="center">{this.getConnectionIcon(network)}</TableCell>
                  </TableRow>
                </TableBody>
                ))}
              </Table>
            </TableContainer>)}
            <Dialog
                open={this.state.show_connect_dialog}
                onClose={this.handelClosDialog}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                  Are you sure you want to connect to '{this.state.selected_network ? this.state.selected_network.ssid : ""  }'?
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                    You'll lose the connection to the robot and will need to connect
                    the same wifi network as the robot to regain access
                    </DialogContentText>
                    {this.state.selected_network && !this.state.selected_network.saved && this.state.selected_network.security !== "" &&
                    (<TextField
                        id="outlined-password-input"
                        label="Password"
                        type="password"
                        onChange={this.onChangePassword}
                      autoComplete="current-password"
                    />)
                    }
                </DialogContent>
                <DialogActions>
                  <Button onClick={this.handleCloseDialog}>Cancel</Button>
                  <Button onClick={this.connectToNetwork} autoFocus>
                    Connect
                  </Button>
                </DialogActions>
            </Dialog>
            <Dialog
                open={this.state.show_forget_dialog}
                onClose={this.handelClosDialog}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                  Are you sure you want to forget network '{this.state.selected_network ? this.state.selected_network.ssid : ""  }'?
                </DialogTitle>
                <DialogActions>
                  <Button onClick={this.handleCloseDialog}>Cancel</Button>
                  <Button onClick={this.forgetNetwork} autoFocus>
                    Forget
                  </Button>
                </DialogActions>
            </Dialog>
        </div>
        );
    }
}

export default Network;