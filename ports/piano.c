#include<math.h>
#include<stdlib.h>
float E(float x){float F[]={0,120,250,600,1200,2500,3500,6000,22050},B[]={-3,-3,0,4,1,0,-3,-6,-8};int i=0;while(i<7&&x>F[i+1])i++;return pow(10,(B[i]+(B[i+1]-B[i])*(x-F[i])/(F[i+1]-F[i]))/20);}
float I(float v,float a,float b,float c){v=v<36?36:v>101?101:v;return v<75?a+(b-a)*(v-36)/39:b+(c-b)*(v-75)/26;}
float*synth(int m,float v,float d,int*L){
 int N=d*44100,P=0,i,j,S=m<=28?1:m<=40?2:3;
 float f0=440*exp2((m-69)/12.),Bb=exp(-7.79+.0653*(m-60)),mx=0,mc=m-60,a=I(v,2.43,2.19,1.84),s=I(v,.04,.088,.094),D=I(v,3,3,2),k=I(v,.02,.035,.06),sl=a+s*mc,A[64],f[64],T[64];
 sl=sl<1.5?1.5:sl>3.6?3.6:sl;
 for(j=0;j<64;j++){float fn=(j+1)*f0*sqrt(1+Bb*(j+1)*(j+1));if(fn>12000)break;f[P]=fn;A[P]=pow(j+1,-sl)/sqrt(1+pow(fn/6e3,4));if(A[P]>mx)mx=A[P];T[P]=fmax(.835*exp(-.0277*mc-.012*(mc>0?mc:0))*pow(f0/fn,.45),.05);P++;}
 for(j=0;j<P;j++)A[j]=A[j]/mx*E(f[j]);
 float*o=calloc(N,4),*z=calloc(N,4),y=0,zm=0;srand(m);
 for(int c=0;c<S;c++){float off=S<2?0:(2.*c/(S-1)-1)*D,mul=exp2(off/1200),ph[64];for(j=0;j<P;j++)ph[j]=rand()*6.2831853/RAND_MAX;
  for(i=0;i<N;i++){float t=i/44100.,x=0;for(j=0;j<P;j++)x+=A[j]*(.85*exp(-t/T[j])+.15*exp(-8*t/T[j]))*sin(6.2831853*f[j]*mul*t+ph[j]);o[i]+=x;}}
 for(i=0;i<N;i++){float u=(rand()+1.)/(RAND_MAX+1.),w=rand()/(float)RAND_MAX,g=sqrt(-2*log(u))*cos(6.2831853*w);y+=.1924*(g-y);z[i]=y;if(fabs(y)>zm)zm=fabs(y);}
 for(i=0;i<N;i++){float t=i/44100.;o[i]=o[i]/S*(1-exp(-t/.004))+k*z[i]/(zm+1e-9)*exp(-t/.006);}
 free(z);*L=N;return o;}
