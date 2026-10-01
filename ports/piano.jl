using Random
function synth(m,v=64,d=3)
 e=m-60
 L(x,X,Y)=x<=X[1] ? Y[1] : x>=X[end] ? Y[end] : (i=findlast(≤(x),X);Y[i]+(Y[i+1]-Y[i])*(x-X[i])/(X[i+1]-X[i]))
 V=[36,75,101]
 a,s,D,k=L(v,V,[2.43,2.19,1.84]),L(v,V,[.04,.088,.094]),L(v,V,[3,3,2]),L(v,V,[.02,.035,.06])
 F=440*2.0^((m-69)/12)
 fr=Float64[];for i=1:64 x=i*F*√(1+exp(-7.79+.0653e)*i^2);x>12000&&break;push!(fr,x) end
 P=length(fr);n=1:P
 A=n.^-clamp(a+s*e,1.5,3.6)./.√(1 .+(fr./6000).^4);A./=maximum(A)
 A.*=[10^(L(q,[0,120,250,600,1200,2500,3500,6000,22050],[-3,-3,0,4,1,0,-3,-6,-8])/20) for q in fr]
 T=max.(.835*exp(-.0277e-.012*max(e,0)).*(F./fr).^.45,.05)
 N=Int(d*44100);t=(0:N-1)./44100;o=zeros(N);r=MersenneTwister(m)
 S=m<=28 ? 1 : m<=40 ? 2 : 3
 for c in (S<2 ? [0] : [(2(i-1)/(S-1)-1)*D for i=1:S])
  ph=2π*rand(r,P);E=A.*(.85*exp.(-t'./T).+.15*exp.(-8 .*t'./T))
  o.+=vec(sum(E.*sin.(2π.*(fr*2.0^(c/1200)).*t'.+ph),dims=1))
 end
 o.=o/S.*(1 .-exp.(-t./.004))
 y=0.0;z=zeros(N);for i=1:N y+=.1924*(randn(r)-y);z[i]=y end
 o.+=k.*z./(maximum(abs.(z))+1e-9).*exp.(-t./.006)
 Float32.(o)
end
