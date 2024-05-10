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
            wifi_status: {},
            wifi_networks: [],
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