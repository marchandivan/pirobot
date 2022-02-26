import Grid from '@material-ui/core/Grid';
import React from 'react';
import Button from '@material-ui/core/Button';
import Stack from '@mui/material/Stack';
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
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p>
                        Arm Controls
                    </p>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={0} direction="row" alignItems="center">
                        <PrecisionManufacturingIcon/>
                        <IconButton onClick={this.props.move_claw_callback.bind(this, this.props.max_angle_claw)}><OpenInFullIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, this.props.position_claw + 5)}><ArrowLeftIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, this.props.position_claw - 5)}><ArrowRightIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_claw_callback.bind(this, 0)}><CloseFullscreenIcon/></IconButton>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_claw}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={0} direction="row" alignItems="center">
                        <ReplayIcon/>
                        <IconButton style={{paddingBlock: 0}} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist - 5)}><FastRewindIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist - 1)}><ArrowLeftIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist + 1)}><ArrowRightIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_wrist_callback.bind(this, this.props.position_wrist + 5)}><FastForwardIcon/></IconButton>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_wrist}°</p>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.lock_wrist_callback}>{this.props.lock_wrist ? (<LockIcon/>) : (<LockOpenIcon/>)}</IconButton>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={0} direction="row" alignItems="center">
                        <ReplayIcon/>
                        <IconButton sx={{ p: 0, m: 0 }} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm - 5)}><FastRewindIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm - 1)}><ArrowLeftIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm + 1)}><ArrowRightIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_forearm_callback.bind(this, this.props.position_forearm + 5)}><FastForwardIcon/></IconButton>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_forearm}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={0} direction="row" alignItems="center">
                        <ThreeSixtyIcon/>
                        <IconButton style={{paddingBlock: 0}} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder - 5)}><FastRewindIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder - 1)}><ArrowLeftIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder + 1)}><ArrowRightIcon/></IconButton>
                        <IconButton style={{paddingBlock: 0}} edge={"start"} onClick={this.props.move_shoulder_callback.bind(this, this.props.position_shoulder + 5)}><FastForwardIcon/></IconButton>
                        <p style={{fontSize: 16, margin: 0}}>{this.props.position_shoulder}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p style={{fontSize: 16}}>Preset</p>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "left_camera")}>Left</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "backup_camera")}>Back</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "right_camera")}>Right</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "pickup")}>Pick</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "grab")}>Grab</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "drop")}>Drop</Button>
                </Grid>
            </Grid>
        )
    }
}

export default ArmControl;
