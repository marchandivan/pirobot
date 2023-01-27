import Grid from '@material-ui/core/Grid';
import React from 'react';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import ThreeSixtyIcon from '@mui/icons-material/ThreeSixty';
import ReplayIcon from '@mui/icons-material/Replay';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import CloseFullscreenIcon from '@mui/icons-material/CloseFullscreen';
import OpenInFullIcon from '@mui/icons-material/OpenInFull';
import IconButton from "@material-ui/core/IconButton";
import ArrowLeftIcon from '@mui/icons-material/ArrowLeft';
import FastRewindIcon from '@mui/icons-material/FastRewind';
import FastForwardIcon from '@mui/icons-material/FastForward';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';

class ArmControl extends React.Component {

    render() {
        if (this.props.hide) {
            return null;
        }
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p style={{fontSize: 16, margin: 10}}>
                        Arm Controls
                        - <IconButton title="Lock wrist" style={{paddingBlock: 0}} edge={"start"} onClick={this.props.lock_wrist_callback}>{this.props.lock_wrist ? (<LockIcon/>) : (<LockOpenIcon/>)}</IconButton>
                    </p>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item xs={2}>
                        <PrecisionManufacturingIcon/>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton onClick={this.props.move_claw_callback.bind(this, this.props.max_angle_claw)}><OpenInFullIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, this.props.position_claw + 5)}><ArrowLeftIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, this.props.position_claw - 5)}><ArrowRightIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, 0)}><CloseFullscreenIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_claw}°</p>
                    </Grid>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item xs={2}>
                        <ReplayIcon/>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist - 5)}><FastRewindIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist - 1)}><ArrowLeftIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist + 1)}><ArrowRightIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist + 5)}><FastForwardIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_wrist}°</p>
                    </Grid>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item xs={2}>
                        <ReplayIcon/>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton sx={{ p: 0, m: 0 }} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm - 5)}><FastRewindIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm - 1)}><ArrowLeftIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm + 1)}><ArrowRightIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm + 5)}><FastForwardIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_forearm}°</p>
                    </Grid>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item xs={2}>
                        <ThreeSixtyIcon/>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder - 5)}><FastRewindIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder - 1)}><ArrowLeftIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder + 1)}><ArrowRightIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder + 5)}><FastForwardIcon/></IconButton>
                    </Grid>
                    <Grid item xs={2}>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_shoulder}°</p>
                    </Grid>
                </Grid>
                <Grid container alignContent="center">
                    <Grid item xl={12} md={12} sm={12} xs={12}>
                        <ButtonGroup fullWidth={true}>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "left_camera")}>Left</Button>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "docking")}>Dock</Button>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "right_camera")}>Right</Button>
                        </ButtonGroup>
                    </Grid>
                    <Grid item xl={12} md={12} sm={12} xs={12}>
                        <ButtonGroup fullWidth={true}>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "left_back_camera")}>Left</Button>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "backup_camera")}>Back</Button>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "right_back_camera")}>Right</Button>
                        </ButtonGroup>
                    </Grid>
                    <Grid item xl={12} md={12} sm={12} xs={12}>
                        <ButtonGroup fullWidth={true}>
                            <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "pickup")}>Pick</Button>
                            <Button style={{fontSize: 10, paddingBlock: 2}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "grab")}>Grab</Button>
                            <Button style={{fontSize: 10, paddingBlock: 2}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "back")}>Back</Button>
                            <Button style={{fontSize: 10, paddingBlock: 2}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "drop")}>Drop</Button>
                        </ButtonGroup>
                    </Grid>
                </Grid>
            </Grid>
        )
    }
}

export default ArmControl;
