//---------------------------------Imports-------------------------------------------------
 //grab the libraries we need
 import ddf.minim.*;
 import ddf.minim.signals.*;
 import ddf.minim.analysis.*;
 import ddf.minim.effects.*;
 
 //-------------------------Initialization of Variables--------------------------------------
 int paddleWidth;
 int paddleLength;
 boolean inplay;
 float[] alphaAverages;
 int averageLength = 50; //averages about the last 5 seconds worth of data
 int counter = 0;
 int hit = 0;
 static int alphaCenter = 9;
 static int alphaBandwidth = 2; //really bandwidth divided by 2
 
 // Constants mainly used for scaling the data to readable sizes
  int windowWidth = 500;
 int windowHeight = 400;
 float scaleFreq = 1.33f;
 
 // Variables used to handle bad data
 boolean absoluteBadDataFlag;
 boolean averageBadDataFlag;
 
 //Parameters for the ball. For both pos and vel, 0 index is x and 1 index is y.
 float[] ballpos = {250,250};
 float ballspeed = 3;
 float[] ballvel = {0,0}; //velocity
 float ballrad = 10;      //radius
 
// Variables used to store data functions/effects
 Minim minim;
 AudioInput in;
 FFT fft;
 BandPass alphaFilter;

//--------------------------Functions------------------------------------------------------
void setup(){
  alphaAverages = new float[averageLength];
  for (int i = 0; i < averageLength; i++){
    alphaAverages[i] = 0;
  }
  
  size(500,400,P2D);
  background(0); //make background black
  stroke(255);   //and everything we draw white
  
  paddleWidth = 5;
  paddleLength = (height-100) / 5;
  
  //initialize minim, as well as our alpha filter
  minim = new Minim(this);
  alphaFilter = new BandPass(alphaCenter / scaleFreq, alphaBandwidth / scaleFreq, 44100);
  
  // Define minim input with filters
  // (type, bufferSize, sampleRate, bitDepth)
  in = minim.getLineIn(Minim.MONO, 32768, 44100, 16);
  in.addEffect(alphaFilter);
  
  // Initialize FFT
  // Frame size of 4,096 samples gives us 2048 frequency bands
  // This gives a bin width of ~21 Hz (giving worse resolution at low freq and better at high freq)
  fft = new FFT(in.bufferSize(), in.sampleRate());
  fft.window(FFT.HAMMING);
}

void draw(){
  background(0); //clear previous drawings
  
  absoluteBadDataFlag = false;
  averageBadDataFlag = false;
  float timeDomainAverage = 0;
  
  fft.forward(in.left); //compute FFT
  line(0,100,windowWidth,100); //line separating time and frequency data
  
  //get a good amount of time data
  for(int i = 0; i < windowWidth; i++){
    if (abs( in .left.get(i * round( in .bufferSize() / windowWidth))) * 50 > .95){
      absoluteBadDataFlag = true;
    }
    
    // Draw the time domain signal (x1, y1, x2, y2) 
    // "50 +" simply keeps the data centered in the screen
    line(i, 50 + in .left.get(i * round( in .bufferSize() / windowWidth)) * 50, 
         i + 1, 50 + in .left.get((i + 1) * round( in .bufferSize() / windowWidth)) * 50);
   
    timeDomainAverage += abs( in .left.get(i * round( in .bufferSize() / windowWidth)));
  }
  
  timeDomainAverage = timeDomainAverage / (windowWidth - 1);
  
  for (int i = 0; i < windowWidth - 1; i++){
    if (abs( in .left.get((i + 1) * round( in .bufferSize() / windowWidth))) > timeDomainAverage * 4)
      averageBadDataFlag = true;
  }
  
  text("absoluteBadDataFlag = " + absoluteBadDataFlag, windowWidth - 170, 20);
  text("averageBadDataFlag = " + averageBadDataFlag, windowWidth - 170, 40);

  
  int lowBound = fft.freqToIndex(alphaCenter - alphaBandwidth);
  int hiBound = fft.freqToIndex(alphaCenter + alphaBandwidth);
  
  lowBound = round(lowBound/scaleFreq);
  hiBound = round(hiBound/scaleFreq);
  
  float avg = 0;
  for (int j = lowBound; j <= hiBound; j++){
    avg += fft.getBand(j);
  }
  
  avg /= (hiBound - lowBound + 1);
  //scale averages a bit
  avg *= 3.3775;
  
  if (absoluteBadDataFlag == false && averageBadDataFlag == false){
    alphaAverages[counter%averageLength] = avg;
  }
  
  float finalAlphaAverage = 0;
  for (int k = 0; k < averageLength; k++){
    finalAlphaAverage += alphaAverages[k];
  }
  finalAlphaAverage = finalAlphaAverage / averageLength;
  finalAlphaAverage = finalAlphaAverage - 200; //base average is around 100, normalize it
                                               //and make the lower half negative
  
  float paddleHeight = height-paddleLength;
  
  paddleHeight += finalAlphaAverage *2; //finalAlphaAverage ranges from about 0 to 200 now,
                                           //we want that to cover window of 0 to 300
  //make sure the paddle doesn't go off-screen
  if (paddleHeight > height - paddleLength)
    paddleHeight = height - paddleLength;
  if (paddleHeight < 100)
    paddleHeight = 100;
    
  text("Alpha waves: " + paddleHeight, windowWidth - 320, 220);
  rect(5,paddleHeight,paddleWidth,paddleLength);
  
  ballpos[0] += ballvel[0];
  ballpos[1] += ballvel[1];
  
  ellipse(ballpos[0], ballpos[1], ballrad, ballrad);
  
  //collision detection with paddle
  if ((ballpos[0] - ballrad > 5) && (ballpos[0] - ballrad < 5 + paddleWidth) && 
  (ballpos[1] < paddleHeight + paddleLength) && (ballpos[1] > paddleHeight)){
    ballvel[0] *= -1;
    float paddleCenter = (paddleHeight + (paddleHeight + paddleLength)) / 2;
    ballvel[1] = -(paddleCenter - ballpos[1])/15;
    hit += 1;
  }
  //collision detection with opposite wall
  if (ballpos[0] + ballrad > width){
    ballvel[0] *= -1;
  }
  //collision with top wall
  if (ballpos[1] < 100 + ballrad || ballpos[1] > height - ballrad){
    ballvel[1] *= -1;
  }
  text("# of hits: " + hit, windowWidth - 290, 280);
  
  inplay = false;
  
  if (ballvel[0] == -ballspeed) {
    inplay = true;
  }
  
  if (paddleHeight >= 220 && hit == 0 && inplay == false || ballpos[0] < 0){
    ballpos[0] = 250;
    ballpos[1] = 250;
    ballvel[0] = -ballspeed;
    ballvel[1] = 0;
    hit = 0;
  }
  
  counter++;
}

void keyPressed(){
}

// Always close Minim audio classes when you are done with them
void stop() { 
    in.close();
    minim.stop();
    super.stop();
}
